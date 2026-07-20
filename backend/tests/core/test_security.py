import uuid

import pytest

from app.core.exceptions import InvalidTokenError
from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from app.models.enums import UserRole


def test_hash_password_uses_argon2() -> None:
    hashed_password = hash_password("ExamplePassword123!")

    assert hashed_password.startswith("$argon2")
    assert hashed_password != "ExamplePassword123!"


def test_verify_password_accepts_correct_password() -> None:
    password = "ExamplePassword123!"
    hashed_password = hash_password(password)

    assert verify_password(password, hashed_password) is True


def test_verify_password_rejects_incorrect_password() -> None:
    hashed_password = hash_password("ExamplePassword123!")

    assert (
        verify_password(
            "WrongPassword123!",
            hashed_password,
        )
        is False
    )


def test_access_token_round_trip() -> None:
    subject = str(uuid.uuid4())

    token, expires_in = create_access_token(
        subject=subject,
        role=UserRole.USER,
    )

    payload = decode_access_token(token)

    assert payload.sub == subject
    assert payload.role == UserRole.USER
    assert payload.type == "access"
    assert expires_in > 0


def test_decode_access_token_rejects_invalid_token() -> None:
    with pytest.raises(InvalidTokenError):
        decode_access_token("not-a-valid-token")