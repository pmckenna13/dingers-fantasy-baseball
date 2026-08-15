from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from jose import JWTError
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db, get_redis
from app.core.security import (
    TokenType,
    create_access_token,
    create_refresh_token,
    decode_token_of_type,
    hash_password,
    is_refresh_token_revoked,
    revoke_refresh_token,
    verify_password,
)
from app.models.user import User
from app.schemas.token import TokenResponse
from app.schemas.user import UserCreate, UserLogin, UserRead

router = APIRouter()

REFRESH_COOKIE_NAME = "refresh_token"
REFRESH_COOKIE_PATH = "/api/v1/auth"


def _set_refresh_cookie(response: Response, refresh_token: str) -> None:
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        path=REFRESH_COOKIE_PATH,
    )


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(payload: UserCreate, db: AsyncSession = Depends(get_db)) -> User:
    existing = await db.execute(select(User).where(User.email == payload.email))
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Email already registered")

    user = User(
        email=payload.email,
        display_name=payload.display_name,
        hashed_password=hash_password(payload.password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: UserLogin,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()

    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    if not user.is_active:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Account is disabled")

    user_id = str(user.id)
    _set_refresh_cookie(response, create_refresh_token(user_id))
    return TokenResponse(access_token=create_access_token(user_id))


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    response: Response,
    refresh_token: str | None = Cookie(default=None, alias=REFRESH_COOKIE_NAME),
    redis: Redis = Depends(get_redis),
) -> TokenResponse:
    if refresh_token is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Missing refresh token")

    try:
        payload = decode_token_of_type(refresh_token, TokenType.REFRESH)
    except JWTError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token") from exc

    if await is_refresh_token_revoked(redis, payload["jti"]):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Refresh token has been revoked")

    # Rotate: invalidate the presented refresh token and issue a new pair.
    await revoke_refresh_token(redis, payload)
    user_id = payload["sub"]
    _set_refresh_cookie(response, create_refresh_token(user_id))
    return TokenResponse(access_token=create_access_token(user_id))


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    response: Response,
    refresh_token: str | None = Cookie(default=None, alias=REFRESH_COOKIE_NAME),
    redis: Redis = Depends(get_redis),
) -> None:
    if refresh_token is not None:
        try:
            payload = decode_token_of_type(refresh_token, TokenType.REFRESH)
            await revoke_refresh_token(redis, payload)
        except JWTError:
            pass  # already invalid/expired — nothing to revoke
    response.delete_cookie(REFRESH_COOKIE_NAME, path=REFRESH_COOKIE_PATH)


@router.get("/me", response_model=UserRead)
async def me(current_user: User = Depends(get_current_user)) -> User:
    return current_user
