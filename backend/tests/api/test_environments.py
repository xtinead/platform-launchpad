from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.environment import Environment
from app.repositories.environment_repository import EnvironmentRepository


ENVIRONMENTS_URL = "/api/v1/environments"


def authorization_headers(access_token: str) -> dict[str, str]:
    """Return bearer-token headers for authenticated API requests."""

    return {
        "Authorization": f"Bearer {access_token}",
    }


def valid_environment_payload(
    *,
    name: str = "developer-sandbox",
) -> dict[str, str]:
    """Return a valid environment creation request body."""

    return {
        "name": name,
        "environment_type": "development",
        "application_version": "1.0.0",
        "description": "Personal development environment",
    }


def test_create_environment_returns_created_environment(
    client: TestClient,
    db_session: Session,
    registered_user: dict[str, object],
    access_token: str,
) -> None:
    response = client.post(
        ENVIRONMENTS_URL,
        headers=authorization_headers(access_token),
        json=valid_environment_payload(),
    )

    assert response.status_code == 201

    body = response.json()

    assert body["owner_id"] == registered_user["id"]
    assert body["name"] == "developer-sandbox"
    assert body["environment_type"] == "development"
    assert body["application_version"] == "1.0.0"
    assert body["description"] == (
        "Personal development environment"
    )
    assert body["status"] == "pending"
    assert body["external_url"] is None
    assert body["metadata"] == {}
    assert body["destroyed_at"] is None
    assert body["id"]
    assert body["created_at"]
    assert body["updated_at"]

    environment: Environment | None = (
        EnvironmentRepository(
            db_session
        ).get_by_owner_and_name(
            owner_id=registered_user["id"],
            name="developer-sandbox",
        )
    )

    assert environment is not None
    assert str(environment.id) == body["id"]
    assert str(environment.owner_id) == registered_user["id"]
    assert environment.name == "developer-sandbox"
    assert environment.application_version == "1.0.0"


def test_create_environment_requires_authentication(
    client: TestClient,
) -> None:
    response = client.post(
        ENVIRONMENTS_URL,
        json=valid_environment_payload(),
    )

    assert response.status_code == 401

    body = response.json()

    assert body["error"]["code"] == "authentication_required"
    assert body["error"]["details"] == {}
    assert body["error"]["request_id"]


def test_create_environment_rejects_duplicate_owner_name(
    client: TestClient,
    access_token: str,
) -> None:
    headers = authorization_headers(access_token)
    payload = valid_environment_payload()

    first_response = client.post(
        ENVIRONMENTS_URL,
        headers=headers,
        json=payload,
    )

    second_response = client.post(
        ENVIRONMENTS_URL,
        headers=headers,
        json=payload,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409

    body = second_response.json()

    assert body["error"]["code"] == (
        "environment_name_already_exists"
    )
    assert body["error"]["details"] == {}
    assert body["error"]["request_id"]


def test_create_environment_rejects_invalid_name(
    client: TestClient,
    access_token: str,
) -> None:
    response = client.post(
        ENVIRONMENTS_URL,
        headers=authorization_headers(access_token),
        json=valid_environment_payload(name="sandbox_test"),
    )

    assert response.status_code == 422

    body = response.json()

    assert body["detail"][0]["loc"] == ["body", "name"]
    assert body["detail"][0]["type"] == "value_error"
    assert (
        "lowercase letters, numbers, and hyphens"
        in body["detail"][0]["msg"]
    )


def test_create_environment_normalizes_name(
    client: TestClient,
    access_token: str,
) -> None:
    response = client.post(
        ENVIRONMENTS_URL,
        headers=authorization_headers(access_token),
        json=valid_environment_payload(
            name="  Developer-Sandbox  ",
        ),
    )

    assert response.status_code == 201
    assert response.json()["name"] == "developer-sandbox"


def test_create_environment_normalizes_editable_fields(
    client: TestClient,
    access_token: str,
) -> None:
    payload = valid_environment_payload()
    payload["application_version"] = "  1.2.3  "
    payload["description"] = "  Development environment  "

    response = client.post(
        ENVIRONMENTS_URL,
        headers=authorization_headers(access_token),
        json=payload,
    )

    assert response.status_code == 201

    body = response.json()

    assert body["application_version"] == "1.2.3"
    assert body["description"] == "Development environment"

def test_list_environments_returns_owner_environments(
    client: TestClient,
    access_token: str,
) -> None:
    headers = authorization_headers(access_token)

    first_response = client.post(
        ENVIRONMENTS_URL,
        headers=headers,
        json=valid_environment_payload(
            name="developer-sandbox",
        ),
    )
    second_response = client.post(
        ENVIRONMENTS_URL,
        headers=headers,
        json=valid_environment_payload(
            name="staging-sandbox",
        ),
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 201

    response = client.get(
        ENVIRONMENTS_URL,
        headers=headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert len(body["items"]) == 2
    assert body["pagination"]["page"] == 1
    assert body["pagination"]["page_size"] == 20
    assert body["pagination"]["total_items"] == 2
    assert body["pagination"]["total_pages"] == 1

    environment_names = {
        item["name"]
        for item in body["items"]
    }

    assert environment_names == {
        "developer-sandbox",
        "staging-sandbox",
    }


def test_list_environments_returns_empty_list(
    client: TestClient,
    access_token: str,
) -> None:
    response = client.get(
        ENVIRONMENTS_URL,
        headers=authorization_headers(access_token),
    )

    assert response.status_code == 200

    body = response.json()

    assert body["items"] == []
    assert body["pagination"] == {
        "page": 1,
        "page_size": 20,
        "total_items": 0,
        "total_pages": 0,
    }


def test_list_environments_requires_authentication(
    client: TestClient,
) -> None:
    response = client.get(ENVIRONMENTS_URL)

    assert response.status_code == 401

    body = response.json()

    assert body["error"]["code"] == "authentication_required"
    assert body["error"]["details"] == {}
    assert body["error"]["request_id"]


def test_list_environments_returns_requested_page(
    client: TestClient,
    access_token: str,
) -> None:
    headers = authorization_headers(access_token)

    for index in range(1, 4):
        response = client.post(
            ENVIRONMENTS_URL,
            headers=headers,
            json=valid_environment_payload(
                name=f"developer-sandbox-{index}",
            ),
        )

        assert response.status_code == 201

    response = client.get(
        ENVIRONMENTS_URL,
        headers=headers,
        params={
            "page": 2,
            "page_size": 2,
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert len(body["items"]) == 1
    assert body["pagination"] == {
        "page": 2,
        "page_size": 2,
        "total_items": 3,
        "total_pages": 2,
    }


def test_list_environments_rejects_invalid_pagination(
    client: TestClient,
    access_token: str,
) -> None:
    response = client.get(
        ENVIRONMENTS_URL,
        headers=authorization_headers(access_token),
        params={
            "page": 0,
            "page_size": 101,
        },
    )

    assert response.status_code == 422

def test_get_environment_returns_environment(
    client: TestClient,
    access_token: str,
) -> None:
    headers = authorization_headers(access_token)

    create_response = client.post(
        ENVIRONMENTS_URL,
        headers=headers,
        json=valid_environment_payload(),
    )

    assert create_response.status_code == 201

    created_environment = create_response.json()
    environment_id = created_environment["id"]

    response = client.get(
        f"{ENVIRONMENTS_URL}/{environment_id}",
        headers=headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == environment_id
    assert body["name"] == "developer-sandbox"
    assert body["environment_type"] == "development"
    assert body["application_version"] == "1.0.0"
    assert body["status"] == "pending"


def test_get_environment_requires_authentication(
    client: TestClient,
    access_token: str,
) -> None:
    create_response = client.post(
        ENVIRONMENTS_URL,
        headers=authorization_headers(access_token),
        json=valid_environment_payload(),
    )

    assert create_response.status_code == 201

    environment_id = create_response.json()["id"]

    response = client.get(
        f"{ENVIRONMENTS_URL}/{environment_id}",
    )

    assert response.status_code == 401

    body = response.json()

    assert body["error"]["code"] == "authentication_required"
    assert body["error"]["details"] == {}
    assert body["error"]["request_id"]


def test_get_environment_returns_not_found_for_missing_environment(
    client: TestClient,
    access_token: str,
) -> None:
    missing_environment_id = (
        "00000000-0000-0000-0000-000000000001"
    )

    response = client.get(
        f"{ENVIRONMENTS_URL}/{missing_environment_id}",
        headers=authorization_headers(access_token),
    )

    assert response.status_code == 404

    body = response.json()

    assert body["error"]["code"] == "environment_not_found"
    assert body["error"]["details"] == {}
    assert body["error"]["request_id"]


def test_get_environment_rejects_invalid_environment_id(
    client: TestClient,
    access_token: str,
) -> None:
    response = client.get(
        f"{ENVIRONMENTS_URL}/not-a-valid-uuid",
        headers=authorization_headers(access_token),
    )

    assert response.status_code == 422


def test_get_environment_denies_access_to_another_users_environment(
    client: TestClient,
    access_token: str,
) -> None:
    owner_headers = authorization_headers(access_token)

    create_response = client.post(
        ENVIRONMENTS_URL,
        headers=owner_headers,
        json=valid_environment_payload(),
    )

    assert create_response.status_code == 201

    environment_id = create_response.json()["id"]

    second_user_payload = {
        "email": "second.user@example.com",
        "password": "SecondPassword123!",
        "full_name": "Second User",
    }

    register_response = client.post(
        "/api/v1/auth/register",
        json=second_user_payload,
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": second_user_payload["email"],
            "password": second_user_payload["password"],
        },
    )

    assert login_response.status_code == 200

    second_user_token = login_response.json()["access_token"]

    response = client.get(
        f"{ENVIRONMENTS_URL}/{environment_id}",
        headers=authorization_headers(second_user_token),
    )

    assert response.status_code == 403

    body = response.json()

    assert body["error"]["code"] == "environment_access_denied"
    assert body["error"]["details"] == {}
    assert body["error"]["request_id"]

def test_update_environment_updates_editable_fields(
    client: TestClient,
    access_token: str,
) -> None:
    headers = authorization_headers(access_token)

    create_response = client.post(
        ENVIRONMENTS_URL,
        headers=headers,
        json=valid_environment_payload(),
    )

    assert create_response.status_code == 201

    created_environment = create_response.json()
    environment_id = created_environment["id"]

    response = client.patch(
        f"{ENVIRONMENTS_URL}/{environment_id}",
        headers=headers,
        json={
            "application_version": "2.0.0",
            "description": "Updated development environment",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == environment_id
    assert body["application_version"] == "2.0.0"
    assert body["description"] == (
        "Updated development environment"
    )
    assert body["name"] == "developer-sandbox"
    assert body["environment_type"] == "development"
    assert body["status"] == "pending"


def test_update_environment_normalizes_fields(
    client: TestClient,
    access_token: str,
) -> None:
    headers = authorization_headers(access_token)

    create_response = client.post(
        ENVIRONMENTS_URL,
        headers=headers,
        json=valid_environment_payload(),
    )

    assert create_response.status_code == 201

    environment_id = create_response.json()["id"]

    response = client.patch(
        f"{ENVIRONMENTS_URL}/{environment_id}",
        headers=headers,
        json={
            "application_version": "  2.1.0  ",
            "description": "  Updated description  ",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["application_version"] == "2.1.0"
    assert body["description"] == "Updated description"


def test_update_environment_allows_description_to_be_cleared(
    client: TestClient,
    access_token: str,
) -> None:
    headers = authorization_headers(access_token)

    create_response = client.post(
        ENVIRONMENTS_URL,
        headers=headers,
        json=valid_environment_payload(),
    )

    assert create_response.status_code == 201

    environment_id = create_response.json()["id"]

    response = client.patch(
        f"{ENVIRONMENTS_URL}/{environment_id}",
        headers=headers,
        json={
            "description": "   ",
        },
    )

    assert response.status_code == 200
    assert response.json()["description"] is None


def test_update_environment_requires_authentication(
    client: TestClient,
    access_token: str,
) -> None:
    create_response = client.post(
        ENVIRONMENTS_URL,
        headers=authorization_headers(access_token),
        json=valid_environment_payload(),
    )

    assert create_response.status_code == 201

    environment_id = create_response.json()["id"]

    response = client.patch(
        f"{ENVIRONMENTS_URL}/{environment_id}",
        json={
            "application_version": "2.0.0",
        },
    )

    assert response.status_code == 401

    body = response.json()

    assert body["error"]["code"] == "authentication_required"
    assert body["error"]["details"] == {}
    assert body["error"]["request_id"]


def test_update_environment_rejects_empty_payload(
    client: TestClient,
    access_token: str,
) -> None:
    headers = authorization_headers(access_token)

    create_response = client.post(
        ENVIRONMENTS_URL,
        headers=headers,
        json=valid_environment_payload(),
    )

    assert create_response.status_code == 201

    environment_id = create_response.json()["id"]

    response = client.patch(
        f"{ENVIRONMENTS_URL}/{environment_id}",
        headers=headers,
        json={},
    )

    assert response.status_code == 422

    body = response.json()

    assert body["detail"][0]["type"] == "value_error"
    assert (
        "At least one environment field must be provided"
        in body["detail"][0]["msg"]
    )


def test_update_environment_returns_not_found(
    client: TestClient,
    access_token: str,
) -> None:
    missing_environment_id = (
        "00000000-0000-0000-0000-000000000001"
    )

    response = client.patch(
        f"{ENVIRONMENTS_URL}/{missing_environment_id}",
        headers=authorization_headers(access_token),
        json={
            "application_version": "2.0.0",
        },
    )

    assert response.status_code == 404

    body = response.json()

    assert body["error"]["code"] == "environment_not_found"
    assert body["error"]["details"] == {}
    assert body["error"]["request_id"]


def test_update_environment_denies_another_user(
    client: TestClient,
    access_token: str,
) -> None:
    owner_headers = authorization_headers(access_token)

    create_response = client.post(
        ENVIRONMENTS_URL,
        headers=owner_headers,
        json=valid_environment_payload(),
    )

    assert create_response.status_code == 201

    environment_id = create_response.json()["id"]

    second_user_payload = {
        "email": "second.update.user@example.com",
        "password": "SecondPassword123!",
        "full_name": "Second Update User",
    }

    register_response = client.post(
        "/api/v1/auth/register",
        json=second_user_payload,
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": second_user_payload["email"],
            "password": second_user_payload["password"],
        },
    )

    assert login_response.status_code == 200

    second_user_token = login_response.json()["access_token"]

    response = client.patch(
        f"{ENVIRONMENTS_URL}/{environment_id}",
        headers=authorization_headers(second_user_token),
        json={
            "application_version": "9.9.9",
        },
    )

    assert response.status_code == 403

    body = response.json()

    assert body["error"]["code"] == "environment_access_denied"
    assert body["error"]["details"] == {}
    assert body["error"]["request_id"]