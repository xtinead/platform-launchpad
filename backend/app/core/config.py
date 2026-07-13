from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Typed application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "Platform Launchpad API"
    app_version: str = "1.0.0"
    app_environment: Literal[
        "development",
        "testing",
        "staging",
        "production",
    ] = "development"

    api_v1_prefix: str = "/api/v1"
    debug: bool = False

    database_url: str

    secret_key: SecretStr
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    cors_origins: list[str] = ["http://localhost:3000"]

    @field_validator("api_v1_prefix")
    @classmethod
    def validate_api_prefix(cls, value: str) -> str:
        if not value.startswith("/"):
            raise ValueError("API_V1_PREFIX must begin with '/'")

        normalized_value = value.rstrip("/")

        if not normalized_value:
            raise ValueError("API_V1_PREFIX cannot be empty")

        return normalized_value


@lru_cache
def get_settings() -> Settings:
    """Return one cached settings instance per application process."""

    return Settings()


settings = get_settings()