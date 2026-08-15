"""JWT issuance, verification, and refresh-token rotation/revocation.

See docs/adr/0001-jwt-over-sessions.md for the rationale: short-lived access
tokens are verified locally (no store lookup on the hot path); refresh tokens
are rotated on every use and can be revoked early via a Redis blocklist keyed
by token id (jti).
"""

import uuid
from datetime import datetime, timedelta, timezone
from enum import Enum

from jose import JWTError, jwt
from passlib.context import CryptContext
from redis.asyncio import Redis

from app.core.config import get_settings

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def _create_token(subject: str, token_type: TokenType, expires_delta: timedelta) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "type": token_type.value,
        "iat": now,
        "exp": now + expires_delta,
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_access_token(user_id: str) -> str:
    return _create_token(
        user_id, TokenType.ACCESS, timedelta(minutes=settings.access_token_expire_minutes)
    )


def create_refresh_token(user_id: str) -> str:
    return _create_token(
        user_id, TokenType.REFRESH, timedelta(days=settings.refresh_token_expire_days)
    )


def decode_token(token: str) -> dict:
    """Raises jose.JWTError if the token is malformed, expired, or has a bad signature."""
    return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])


def decode_token_of_type(token: str, expected_type: TokenType) -> dict:
    payload = decode_token(token)
    if payload.get("type") != expected_type.value:
        raise JWTError(f"expected a {expected_type.value} token")
    return payload


def _blocklist_key(jti: str) -> str:
    return f"revoked_refresh_jti:{jti}"


async def revoke_refresh_token(redis: Redis, payload: dict) -> None:
    """Blocklist a refresh token's jti until its natural expiry, so replay
    after logout / rotation is rejected without needing a full session store.
    """
    ttl_seconds = max(int(payload["exp"] - datetime.now(timezone.utc).timestamp()), 1)
    await redis.set(_blocklist_key(payload["jti"]), "1", ex=ttl_seconds)


async def is_refresh_token_revoked(redis: Redis, jti: str) -> bool:
    return await redis.exists(_blocklist_key(jti)) == 1
