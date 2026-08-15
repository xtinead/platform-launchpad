from fastapi.testclient import TestClient


ENVIRONMENTS_URL = "/api/v1/environments"
DEPLOYMENT_REQUESTS_URL = "/api/v1/deployment-requests"


def authorization_headers(access_token: str) -> dict[str, str]:
    """Return bearer-token headers."""

    return {
        "Authorization": f"Bearer {access_token}",
    }


def environment_payload(
    *,
    name: str = "deployment-sandbox",
) -> dict[str, str]:
    """Return a valid environment request."""

    return {
        "name": name,
        "environment_type": "development",
        "application_version": "1.0.0",
        "description": "Deployment workflow test environment",
    }


def create_environment(
    client: TestClient,
    access_token: str,
    *,
    name: str = "deployment-sandbox",
) -> dict[str, object]:
    """Create and return an environment."""

    response = client.post(
        ENVIRONMENTS_URL,
        headers=authorization_headers(access_token),
        json=environment_payload(name=name),
    )

    assert response.status_code == 201

    return response.json()


def queue_deployment_request(
    client: TestClient,
    access_token: str,
    environment_id: str,
    *,
    operation: str = "provision",
    request_payload: dict[str, object] | None = None,
) -> dict[str, object]:
    """Queue and return a deployment request response."""

    response = client.post(
        (
            f"{ENVIRONMENTS_URL}/{environment_id}"
            "/deployment-requests"
        ),
        headers=authorization_headers(access_token),
        json={
            "operation": operation,
            "request_payload": request_payload or {},
        },
    )

    assert response.status_code == 202

    return response.json()


def register_and_login_second_user(
    client: TestClient,
) -> str:
    """Create a second user and return its token."""

    payload = {
        "email": "deployment.second@example.com",
        "password": "SecondPassword123!",
        "full_name": "Deployment Second User",
    }

    register_response = client.post(
        "/api/v1/auth/register",
        json=payload,
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": payload["email"],
            "password": payload["password"],
        },
    )

    assert login_response.status_code == 200

    return login_response.json()["access_token"]


def test_queue_deployment_request_returns_accepted_response(
    client: TestClient,
    registered_user: dict[str, object],
    access_token: str,
) -> None:
    environment = create_environment(
        client,
        access_token,
    )

    response = client.post(
        (
            f"{ENVIRONMENTS_URL}/{environment['id']}"
            "/deployment-requests"
        ),
        headers=authorization_headers(access_token),
        json={
            "operation": "provision",
            "request_payload": {
                "requested_version": "1.0.0",
            },
        },
    )

    assert response.status_code == 202

    body = response.json()
    deployment_request = body["deployment_request"]

    assert body["environment"]["id"] == environment["id"]
    assert body["environment"]["status"] == "pending"

    assert deployment_request["environment_id"] == environment["id"]
    assert deployment_request["requested_by_id"] == registered_user["id"]
    assert deployment_request["operation"] == "provision"
    assert deployment_request["status"] == "queued"
    assert deployment_request["attempt_count"] == 0
    assert deployment_request["error_message"] is None
    assert deployment_request["request_payload"] == {
        "requested_version": "1.0.0",
    }
    assert deployment_request["requested_at"]
    assert deployment_request["started_at"] is None
    assert deployment_request["completed_at"] is None


def test_queue_deployment_request_requires_authentication(
    client: TestClient,
    access_token: str,
) -> None:
    environment = create_environment(
        client,
        access_token,
    )

    response = client.post(
        (
            f"{ENVIRONMENTS_URL}/{environment['id']}"
            "/deployment-requests"
        ),
        json={
            "operation": "provision",
        },
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == (
        "authentication_required"
    )


def test_queue_deployment_request_returns_not_found(
    client: TestClient,
    access_token: str,
) -> None:
    response = client.post(
        (
            f"{ENVIRONMENTS_URL}/"
            "00000000-0000-0000-0000-000000000001"
            "/deployment-requests"
        ),
        headers=authorization_headers(access_token),
        json={
            "operation": "provision",
        },
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == (
        "environment_not_found"
    )


def test_queue_deployment_request_denies_another_user(
    client: TestClient,
    access_token: str,
) -> None:
    environment = create_environment(
        client,
        access_token,
    )

    second_user_token = register_and_login_second_user(client)

    response = client.post(
        (
            f"{ENVIRONMENTS_URL}/{environment['id']}"
            "/deployment-requests"
        ),
        headers=authorization_headers(second_user_token),
        json={
            "operation": "provision",
        },
    )

    assert response.status_code == 403
    assert response.json()["error"]["code"] == (
        "environment_access_denied"
    )


def test_queue_deployment_request_rejects_duplicate_active_request(
    client: TestClient,
    access_token: str,
) -> None:
    environment = create_environment(
        client,
        access_token,
    )

    first_response = client.post(
        (
            f"{ENVIRONMENTS_URL}/{environment['id']}"
            "/deployment-requests"
        ),
        headers=authorization_headers(access_token),
        json={
            "operation": "provision",
        },
    )

    second_response = client.post(
        (
            f"{ENVIRONMENTS_URL}/{environment['id']}"
            "/deployment-requests"
        ),
        headers=authorization_headers(access_token),
        json={
            "operation": "provision",
        },
    )

    assert first_response.status_code == 202
    assert second_response.status_code == 409
    assert second_response.json()["error"]["code"] == (
        "active_deployment_request_exists"
    )


def test_queue_deployment_request_rejects_invalid_operation_for_state(
    client: TestClient,
    access_token: str,
) -> None:
    environment = create_environment(
        client,
        access_token,
    )

    response = client.post(
        (
            f"{ENVIRONMENTS_URL}/{environment['id']}"
            "/deployment-requests"
        ),
        headers=authorization_headers(access_token),
        json={
            "operation": "upgrade",
        },
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == (
        "invalid_deployment_operation"
    )


def test_queue_deployment_request_rejects_unknown_operation(
    client: TestClient,
    access_token: str,
) -> None:
    environment = create_environment(
        client,
        access_token,
    )

    response = client.post(
        (
            f"{ENVIRONMENTS_URL}/{environment['id']}"
            "/deployment-requests"
        ),
        headers=authorization_headers(access_token),
        json={
            "operation": "restart",
        },
    )

    assert response.status_code == 422


def test_list_deployment_requests_returns_owner_requests(
    client: TestClient,
    access_token: str,
) -> None:
    environment = create_environment(
        client,
        access_token,
    )

    queued_response = queue_deployment_request(
        client,
        access_token,
        str(environment["id"]),
        request_payload={
            "requested_version": "1.0.0",
        },
    )

    response = client.get(
        DEPLOYMENT_REQUESTS_URL,
        headers=authorization_headers(access_token),
    )

    assert response.status_code == 200

    body = response.json()

    assert len(body["items"]) == 1
    assert body["items"][0]["id"] == (
        queued_response["deployment_request"]["id"]
    )
    assert body["items"][0]["operation"] == "provision"
    assert body["items"][0]["status"] == "queued"

    assert body["pagination"] == {
        "page": 1,
        "page_size": 20,
        "total_items": 1,
        "total_pages": 1,
    }


def test_list_deployment_requests_returns_empty_list(
    client: TestClient,
    access_token: str,
) -> None:
    response = client.get(
        DEPLOYMENT_REQUESTS_URL,
        headers=authorization_headers(access_token),
    )

    assert response.status_code == 200

    assert response.json() == {
        "items": [],
        "pagination": {
            "page": 1,
            "page_size": 20,
            "total_items": 0,
            "total_pages": 0,
        },
    }


def test_list_deployment_requests_requires_authentication(
    client: TestClient,
) -> None:
    response = client.get(DEPLOYMENT_REQUESTS_URL)

    assert response.status_code == 401
    assert response.json()["error"]["code"] == (
        "authentication_required"
    )


def test_list_deployment_requests_filters_by_status(
    client: TestClient,
    access_token: str,
) -> None:
    environment = create_environment(
        client,
        access_token,
    )

    queue_deployment_request(
        client,
        access_token,
        str(environment["id"]),
    )

    queued_response = client.get(
        DEPLOYMENT_REQUESTS_URL,
        headers=authorization_headers(access_token),
        params={
            "status": "queued",
        },
    )

    succeeded_response = client.get(
        DEPLOYMENT_REQUESTS_URL,
        headers=authorization_headers(access_token),
        params={
            "status": "succeeded",
        },
    )

    assert queued_response.status_code == 200
    assert succeeded_response.status_code == 200

    assert queued_response.json()["pagination"]["total_items"] == 1
    assert succeeded_response.json()["pagination"]["total_items"] == 0


def test_list_deployment_requests_filters_by_operation(
    client: TestClient,
    access_token: str,
) -> None:
    environment = create_environment(
        client,
        access_token,
    )

    queue_deployment_request(
        client,
        access_token,
        str(environment["id"]),
        operation="provision",
    )

    provision_response = client.get(
        DEPLOYMENT_REQUESTS_URL,
        headers=authorization_headers(access_token),
        params={
            "operation": "provision",
        },
    )

    destroy_response = client.get(
        DEPLOYMENT_REQUESTS_URL,
        headers=authorization_headers(access_token),
        params={
            "operation": "destroy",
        },
    )

    assert provision_response.status_code == 200
    assert destroy_response.status_code == 200

    assert provision_response.json()["pagination"]["total_items"] == 1
    assert destroy_response.json()["pagination"]["total_items"] == 0


def test_list_deployment_requests_is_owner_scoped(
    client: TestClient,
    access_token: str,
) -> None:
    environment = create_environment(
        client,
        access_token,
    )

    queue_deployment_request(
        client,
        access_token,
        str(environment["id"]),
    )

    second_user_token = register_and_login_second_user(client)

    response = client.get(
        DEPLOYMENT_REQUESTS_URL,
        headers=authorization_headers(second_user_token),
    )

    assert response.status_code == 200
    assert response.json()["items"] == []
    assert response.json()["pagination"]["total_items"] == 0


def test_get_deployment_request_returns_request(
    client: TestClient,
    access_token: str,
) -> None:
    environment = create_environment(
        client,
        access_token,
    )

    operation_response = queue_deployment_request(
        client,
        access_token,
        str(environment["id"]),
    )

    deployment_request = operation_response["deployment_request"]

    response = client.get(
        f"{DEPLOYMENT_REQUESTS_URL}/{deployment_request['id']}",
        headers=authorization_headers(access_token),
    )

    assert response.status_code == 200
    assert response.json()["id"] == deployment_request["id"]
    assert response.json()["environment_id"] == environment["id"]
    assert response.json()["status"] == "queued"


def test_get_deployment_request_requires_authentication(
    client: TestClient,
    access_token: str,
) -> None:
    environment = create_environment(
        client,
        access_token,
    )

    operation_response = queue_deployment_request(
        client,
        access_token,
        str(environment["id"]),
    )

    deployment_request_id = operation_response[
        "deployment_request"
    ]["id"]

    response = client.get(
        f"{DEPLOYMENT_REQUESTS_URL}/{deployment_request_id}",
    )

    assert response.status_code == 401


def test_get_deployment_request_returns_not_found(
    client: TestClient,
    access_token: str,
) -> None:
    response = client.get(
        (
            f"{DEPLOYMENT_REQUESTS_URL}/"
            "00000000-0000-0000-0000-000000000001"
        ),
        headers=authorization_headers(access_token),
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == (
        "deployment_request_not_found"
    )


def test_get_deployment_request_rejects_invalid_id(
    client: TestClient,
    access_token: str,
) -> None:
    response = client.get(
        f"{DEPLOYMENT_REQUESTS_URL}/not-a-valid-uuid",
        headers=authorization_headers(access_token),
    )

    assert response.status_code == 422


def test_get_deployment_request_denies_another_user(
    client: TestClient,
    access_token: str,
) -> None:
    environment = create_environment(
        client,
        access_token,
    )

    operation_response = queue_deployment_request(
        client,
        access_token,
        str(environment["id"]),
    )

    deployment_request_id = operation_response[
        "deployment_request"
    ]["id"]

    second_user_token = register_and_login_second_user(client)

    response = client.get(
        f"{DEPLOYMENT_REQUESTS_URL}/{deployment_request_id}",
        headers=authorization_headers(second_user_token),
    )

    assert response.status_code == 403
    assert response.json()["error"]["code"] == (
        "deployment_request_access_denied"
    )