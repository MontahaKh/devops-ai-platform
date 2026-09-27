from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    app_name: str = "DevOps AI Platform API"
    app_env: Literal["development", "testing", "production"] = "development"
    debug: bool = Field(default=False, validation_alias="APP_DEBUG")
    database_url: PostgresDsn
    jwt_secret_key: str = Field(min_length=32)
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = Field(default=30, gt=0)
    redis_url: str = "redis://localhost:6379/0"
    task_queue_enabled: bool = False
    run_timeout_seconds: int = Field(default=300, gt=0)
    run_max_retries: int = Field(default=2, ge=0, le=10)

    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
