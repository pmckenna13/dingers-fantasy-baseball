from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralized app config, loaded from environment variables / .env.

    Kept as a single lru_cache'd Settings object so FastAPI dependencies can
    request it cheaply without re-parsing the environment per-request.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: str = "local"

    database_url: str = "postgresql+asyncpg://fantasy:fantasy@localhost:5432/fantasy_baseball"
    redis_url: str = "redis://localhost:6379/0"

    # No default: this repo is public, so a hardcoded fallback here would be
    # a known-to-everyone JWT signing secret. Must come from the environment
    # (.env locally, CI secrets in CI, Secrets Manager in real deployments) —
    # missing it should fail startup loudly, not sign tokens with a public value.
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    cors_origins: str = "http://localhost:5173"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
