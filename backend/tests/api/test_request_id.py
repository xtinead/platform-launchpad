import uuid

from fastapi.testclient import TestClient


REQUEST_ID_HEADER = "X-Request-ID"


def test_response_contains_generated_request_id(
    client: TestClient,
) -> None:
    response = client.get("/health/live")

    assert response.status_code == 200
    assert REQUEST_ID_HEADER in response.headers

    generated_request_id = response.headers[REQUEST_ID_HEADER]

    assert str(uuid.UUID(generated_request_id)) == generated_request_id


def test_valid_request_id_is_preserved(
    client: TestClient,
) -> None:
    request_id = "55e329f7-f67e-4ca8-a136-52b172362f06"

    response = client.get(
        "/health/live",
        headers={
            REQUEST_ID_HEADER: request_id,
        },
    )

    assert response.status_code == 200
    assert response.headers[REQUEST_ID_HEADER] == request_id


def test_invalid_request_id_is_replaced(
    client: TestClient,
) -> None:
    response = client.get(
        "/health/live",
        headers={
            REQUEST_ID_HEADER: "not-a-valid-uuid",
        },
    )

    assert response.status_code == 200

    response_request_id = response.headers[REQUEST_ID_HEADER]

    assert response_request_id != "not-a-valid-uuid"
    assert str(uuid.UUID(response_request_id)) == response_request_id


def test_error_body_and_header_share_request_id(
    client: TestClient,
) -> None:
    response = client.get("/api/v1/users/me")

    assert response.status_code == 401

    header_request_id = response.headers[REQUEST_ID_HEADER]
    body_request_id = response.json()["error"]["request_id"]

    assert header_request_id == body_request_id