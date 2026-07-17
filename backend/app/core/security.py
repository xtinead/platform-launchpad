from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from jwt import ExpiredSignatureError, InvalidTokenError as PyJWTInvalidTokenError
from pwdlib import PasswordHash
from pwdlib.exceptions import UnknownHashError

from app.core.config import settings
from app.core.exceptions import InvalidTokenError, TokenExpiredError
from app.models.enums import UserRole
from app.schemas.auth import TokenPayload


password_hash = PasswordHash.recommended()


def hash_password(plain_password: str) -> str:
    """Return a secure Argon2 password hash."""

    return password_hash.hash(plain_password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    """Return whether a plaintext password matches a stored hash."""

    try:
        return password_hash.verify(
            plain_password,
            hashed_password,
        )
    except UnknownHashError:
        return False


def create_access_token(
    *,
    subject: str,
    role: UserRole | str,
) -> tuple[str, int]:
    """Create a signed, short-lived JWT access token."""

    now = datetime.now(UTC)
    expires_delta = timedelta(
        minutes=settings.access_token_expire_minutes,
    )
    expires_at = now + expires_delta

    normalized_role = (
        role if isinstance(role, UserRole) else UserRole(role)
    )

    payload: dict[str, Any] = {
        "sub": subject,
        "role": normalized_role.value,
        "type": "access",
        "iat": now,
        "exp": expires_at,
    }

    encoded_token = jwt.encode(
        payload,
        settings.secret_key.get_secret_value(),
        algorithm=settings.jwt_algorithm,
    )

    return encoded_token, int(expires_delta.total_seconds())

def decode_access_token(token: str) -> TokenPayload:
    """Validate and decode an access token."""

    try:
        payload = jwt.decode(
            token,
            settings.secret_key.get_secret_value(),
            algorithms=[settings.jwt_algorithm],
            options={
                "require": [
                    "sub",
                    "role",
                    "type",
                    "iat",
                    "exp",
                ]
            },
        )
    except ExpiredSignatureError as exc:
        raise TokenExpiredError() from exc
    except PyJWTInvalidTokenError as exc:
        raise InvalidTokenError() from exc

    try:
        token_payload = TokenPayload.model_validate(payload)
    except ValueError as exc:
        raise InvalidTokenError() from exc

    if token_payload.type != "access":
        raise InvalidTokenError()

    return token_payload