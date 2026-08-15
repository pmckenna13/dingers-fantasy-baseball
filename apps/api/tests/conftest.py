from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.core.deps import get_redis
from app.db.base import Base
from app.db.session import get_db
from app.main import app

# In-memory SQLite for fast, isolated test runs — Postgres-specific types
# (like UUID) still round-trip fine via SQLAlchemy's generic UUID handling.
TEST_DATABASE_URL = "sqlite+aiosqlite://"


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    engine = create_async_engine(TEST_DATABASE_URL, poolclass=StaticPool)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session

    await engine.dispose()


class FakeRedis:
    """Minimal in-memory stand-in for redis.asyncio.Redis, enough for the
    refresh-token blocklist calls exercised in tests (set/exists)."""

    def __init__(self) -> None:
        self._store: dict[str, str] = {}

    async def set(self, key: str, value: str, ex: int | None = None) -> None:
        del ex  # unused: real Redis TTL isn't needed for these test assertions
        self._store[key] = value

    async def exists(self, key: str) -> int:
        return 1 if key in self._store else 0


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def _get_db_override() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    fake_redis = FakeRedis()  # one instance per test, shared across requests

    async def _get_redis_override() -> AsyncGenerator[FakeRedis, None]:
        yield fake_redis

    app.dependency_overrides[get_db] = _get_db_override
    app.dependency_overrides[get_redis] = _get_redis_override

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
