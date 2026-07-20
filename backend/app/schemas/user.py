import re
import uuid
from datetime import datetime

from pydantic import EmailStr, Field, SecretStr, field_validator

from app.models.enums import UserRole
from app.schemas.common import APIModel


PASSWORD_UPPERCASE_PATTERN = re.compile(r"[A-Z]")
PASSWORD_LOWERCASE_PATTERN = re.compile(r"[a-z]")
PASSWORD_NUMBER_PATTERN = re.compile(r"\d")
PASSWORD_SPECIAL_PATTERN = re.compile(r"[^A-Za-z0-9]")


def validate_password_strength(password: str) -> str:
    """Validate the approved Platform Launchpad password policy."""

    if len(password) < 12:
        raise ValueError("Password must contain at least 12 characters.")

    if len(password) > 128:
        raise ValueError("Password must contain no more than 128 characters.")

    if not PASSWORD_UPPERCASE_PATTERN.search(password):
        raise ValueError("Password must contain an uppercase letter.")

    if not PASSWORD_LOWERCASE_PATTERN.search(password):
        raise ValueError("Password must contain a lowercase letter.")

    if not PASSWORD_NUMBER_PATTERN.search(password):
        raise ValueError("Password must contain a number.")

    if not PASSWORD_SPECIAL_PATTERN.search(password):
        raise ValueError("Password must contain a special character.")

    return password


class UserRegistrationRequest(APIModel):
    email: EmailStr
    password: SecretStr
    full_name: str = Field(min_length=2, max_length=150)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return str(value).strip().lower()

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: SecretStr) -> SecretStr:
        validate_password_strength(value.get_secret_value())
        return value


class UserSummary(APIModel):
    id: uuid.UUID
    email: EmailStr
    full_name: str
    role: UserRole
    is_active: bool


class UserResponse(UserSummary):
    created_at: datetime
    updated_at: datetime
    last_login_at: datetime | None = None


class AdminUserUpdateRequest(APIModel):
    is_active: bool