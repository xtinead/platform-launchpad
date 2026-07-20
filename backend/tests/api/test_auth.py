from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.user_repository import UserRepository


def test_register_user_returns_created_user(
    client: TestClient,
    db_session: Session,
    registered_user_payload: dict[str, str],
) -> None:
    response = client.post(
        "/api/v1/auth/register",
        json=registered_user_payload,
    )

    assert response.status_code == 201

    body = response.json()

    assert body["email"] == "developer@example.com"
    assert body["full_name"] == "Example Developer"
    assert body["role"] == "user"
    assert body["is_active"] is True
    assert body["last_login_at"] is None
    assert "password" not in body
    assert "password_hash" not in body

    user = UserRepository(db_session).get_by_email(
        "developer@example.com"
    )

    assert user is not None
    assert user.password_hash.startswith("$argon2")
    assert user.password_hash != registered_user_payload["password"]


def test_register_user_rejects_duplicate_email(
    client: TestClient,
    registered_user_payload: dict[str, str],
) -> None:
    first_response = client.post(
        "/api/v1/auth/register",
        json=registered_user_payload,
    )
    second_response = client.post(
        "/api/v1/auth/register",
        json=registered_user_payload,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409

    body = second_response.json()

    assert body["error"]["code"] == "email_already_registered"
    assert body["error"]["details"] == {}
    assert body["error"]["request_id"]


def test_register_user_normalizes_email(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "Developer@Example.COM",
            "password": "ExamplePassword123!",
            "full_name": "Example Developer",
        },
    )

    assert response.status_code == 201
    assert response.json()["email"] == "developer@example.com"


def test_login_returns_access_token(
    client: TestClient,
    registered_user: dict[str, object],
    registered_user_payload: dict[str, str],
) -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": registered_user_payload["email"],
            "password": registered_user_payload["password"],
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert isinstance(body["access_token"], str)
    assert body["access_token"]
    assert body["token_type"] == "bearer"
    assert body["expires_in"] > 0
    assert body["user"]["email"] == "developer@example.com"


def test_login_updates_last_login_timestamp(
    client: TestClient,
    db_session: Session,
    registered_user: dict[str, object],
    registered_user_payload: dict[str, str],
) -> None:
    user: User | None = UserRepository(
        db_session
    ).get_by_email("developer@example.com")

    assert user is not None
    assert user.last_login_at is None

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": registered_user_payload["email"],
            "password": registered_user_payload["password"],
        },
    )

    assert response.status_code == 200

    db_session.refresh(user)

    assert user.last_login_at is not None


def test_login_rejects_incorrect_password(
    client: TestClient,
    registered_user: dict[str, object],
    registered_user_payload: dict[str, str],
) -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": registered_user_payload["email"],
            "password": "WrongPassword123!",
        },
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "invalid_credentials"


def test_login_rejects_unknown_email(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "missing@example.com",
            "password": "ExamplePassword123!",
        },
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "invalid_credentials"