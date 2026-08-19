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

    database_url: str | None = None
    database_url_file: Path | None = None

    test_database_url: str | None = None

    secret_key: SecretStr | None = None
    secret_key_file: Path | None = None

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

    def resolved_database_url(self) -> str:
        """Return the configured database URL."""

        if self.database_url:
            return self.database_url

        if self.database_url_file:
            return self.database_url_file.read_text(
                encoding="utf-8"
            ).strip()

        raise ValueError(
            "DATABASE_URL or DATABASE_URL_FILE must be configured."
        )

    def resolved_secret_key(self) -> SecretStr:
        """Return the configured application secret key."""

        if self.secret_key:
            return self.secret_key

        if self.secret_key_file:
            value = self.secret_key_file.read_text(
                encoding="utf-8"
            ).strip()

            if value:
                return SecretStr(value)

        raise ValueError(
            "SECRET_KEY or SECRET_KEY_FILE must be configured."
        )


@lru_cache
def get_settings() -> Settings:
    """Return one cached settings instance per application process."""

    return Settings()


settings = get_settings()