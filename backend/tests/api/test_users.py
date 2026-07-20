from fastapi.testclient import TestClient


def test_get_current_user_returns_authenticated_profile(
    client: TestClient,
    registered_user: dict[str, object],
    access_token: str,
) -> None:
    response = client.get(
        "/api/v1/users/me",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == registered_user["id"]
    assert body["email"] == registered_user["email"]
    assert body["role"] == "user"
    assert "password_hash" not in body


def test_get_current_user_requires_authentication(
    client: TestClient,
) -> None:
    response = client.get("/api/v1/users/me")

    assert response.status_code == 401
    assert response.json()["error"]["code"] == (
        "authentication_required"
    )


def test_get_current_user_rejects_invalid_token(
    client: TestClient,
) -> None:
    response = client.get(
        "/api/v1/users/me",
        headers={
            "Authorization": "Bearer invalid-token",
        },
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "invalid_token"