from typing import Any

import pytest
from sqlalchemy.orm import Session

from app.models.deployment_request import DeploymentRequest
from app.models.environment import Environment
from app.models.enums import (
    DeploymentOperation,
    DeploymentRequestStatus,
    EnvironmentStatus,
    EnvironmentType,
)
from app.models.user import User
from app.services.deployment_executor import (
    DeploymentExecutionError,
    DeploymentExecutionResult,
    DeploymentExecutor,
)
from app.services.deployment_worker_service import (
    DeploymentWorkerService,
)


class SuccessfulExecutor(DeploymentExecutor):
    """Return deterministic metadata for successful worker tests."""

    def execute(
        self,
        deployment_request: DeploymentRequest,
    ) -> DeploymentExecutionResult:
        operation = DeploymentOperation(
            deployment_request.operation
        )

        return DeploymentExecutionResult(
            metadata={
                "executor": "test",
                "operation": operation.value,
                "resource_id": "test-resource-123",
            },
        )


class FailingExecutor(DeploymentExecutor):
    """Raise a controlled infrastructure-execution failure."""

    def execute(
        self,
        deployment_request: DeploymentRequest,
    ) -> DeploymentExecutionResult:
        raise DeploymentExecutionError(
            "Simulated infrastructure failure."
        )


class UnexpectedFailingExecutor(DeploymentExecutor):
    """Raise an unexpected execution exception."""

    def execute(
        self,
        deployment_request: DeploymentRequest,
    ) -> DeploymentExecutionResult:
        raise RuntimeError("Unexpected executor failure.")


def create_environment_model(
    db_session: Session,
    user: User,
    *,
    name: str,
    status: EnvironmentStatus = EnvironmentStatus.PENDING,
) -> Environment:
    """Persist an environment for worker-service tests."""

    environment = Environment(
        owner_id=user.id,
        name=name,
        environment_type=EnvironmentType.DEVELOPMENT,
        application_version="1.0.0",
        description="Worker service test environment",
        status=status,
        platform_metadata={},
    )

    db_session.add(environment)
    db_session.commit()
    db_session.refresh(environment)

    return environment


def create_deployment_request_model(
    db_session: Session,
    user: User,
    environment: Environment,
    *,
    operation: DeploymentOperation,
    status: DeploymentRequestStatus = (
        DeploymentRequestStatus.QUEUED
    ),
    request_payload: dict[str, Any] | None = None,
) -> DeploymentRequest:
    """Persist a deployment request for worker-service tests."""

    deployment_request = DeploymentRequest(
        environment_id=environment.id,
        requested_by_id=user.id,
        operation=operation,
        status=status,
        attempt_count=0,
        request_payload=request_payload or {},
    )

    db_session.add(deployment_request)
    db_session.commit()
    db_session.refresh(deployment_request)

    return deployment_request


def test_claim_next_request_marks_request_processing(
    db_session: Session,
    test_user: User,
) -> None:
    environment = create_environment_model(
        db_session,
        test_user,
        name="claim-request-environment",
    )

    deployment_request = create_deployment_request_model(
        db_session,
        test_user,
        environment,
        operation=DeploymentOperation.PROVISION,
    )

    result = DeploymentWorkerService(
        db_session,
        executor=SuccessfulExecutor(),
    ).claim_next_request()

    assert result is not None
    assert result.id == deployment_request.id
    assert result.status == DeploymentRequestStatus.PROCESSING
    assert result.attempt_count == 1
    assert result.started_at is not None
    assert result.completed_at is None
    assert result.error_message is None

    db_session.refresh(environment)

    assert environment.status == EnvironmentStatus.PROVISIONING


def test_claim_next_destroy_request_marks_environment_destroying(
    db_session: Session,
    test_user: User,
) -> None:
    environment = create_environment_model(
        db_session,
        test_user,
        name="destroy-claim-environment",
        status=EnvironmentStatus.ACTIVE,
    )

    deployment_request = create_deployment_request_model(
        db_session,
        test_user,
        environment,
        operation=DeploymentOperation.DESTROY,
    )

    result = DeploymentWorkerService(
        db_session,
        executor=SuccessfulExecutor(),
    ).claim_next_request()

    assert result is not None
    assert result.id == deployment_request.id
    assert result.status == DeploymentRequestStatus.PROCESSING

    db_session.refresh(environment)

    assert environment.status == EnvironmentStatus.DESTROYING


def test_claim_next_request_returns_none_when_queue_empty(
    db_session: Session,
) -> None:
    result = DeploymentWorkerService(
        db_session,
        executor=SuccessfulExecutor(),
    ).claim_next_request()

    assert result is None


def test_process_next_provision_request_succeeds(
    db_session: Session,
    test_user: User,
) -> None:
    environment = create_environment_model(
        db_session,
        test_user,
        name="successful-provision-environment",
    )

    deployment_request = create_deployment_request_model(
        db_session,
        test_user,
        environment,
        operation=DeploymentOperation.PROVISION,
    )

    result = DeploymentWorkerService(
        db_session,
        executor=SuccessfulExecutor(),
    ).process_next_request()

    assert result is not None
    assert result.id == deployment_request.id
    assert result.status == DeploymentRequestStatus.SUCCEEDED
    assert result.attempt_count == 1
    assert result.started_at is not None
    assert result.completed_at is not None
    assert result.error_message is None

    db_session.refresh(environment)

    assert environment.status == EnvironmentStatus.ACTIVE
    assert environment.destroyed_at is None
    assert environment.platform_metadata == {
        "executor": "test",
        "operation": "provision",
        "resource_id": "test-resource-123",
    }


def test_process_next_destroy_request_succeeds(
    db_session: Session,
    test_user: User,
) -> None:
    environment = create_environment_model(
        db_session,
        test_user,
        name="successful-destroy-environment",
        status=EnvironmentStatus.ACTIVE,
    )
    environment.external_url = "https://example.test"
    db_session.commit()

    deployment_request = create_deployment_request_model(
        db_session,
        test_user,
        environment,
        operation=DeploymentOperation.DESTROY,
    )

    result = DeploymentWorkerService(
        db_session,
        executor=SuccessfulExecutor(),
    ).process_next_request()

    assert result is not None
    assert result.id == deployment_request.id
    assert result.status == DeploymentRequestStatus.SUCCEEDED
    assert result.completed_at is not None

    db_session.refresh(environment)

    assert environment.status == EnvironmentStatus.DESTROYED
    assert environment.destroyed_at is not None
    assert environment.external_url is None
    assert environment.platform_metadata["operation"] == "destroy"


def test_process_next_request_handles_execution_failure(
    db_session: Session,
    test_user: User,
) -> None:
    environment = create_environment_model(
        db_session,
        test_user,
        name="failed-provision-environment",
    )

    deployment_request = create_deployment_request_model(
        db_session,
        test_user,
        environment,
        operation=DeploymentOperation.PROVISION,
    )

    result = DeploymentWorkerService(
        db_session,
        executor=FailingExecutor(),
    ).process_next_request()

    assert result is not None
    assert result.id == deployment_request.id
    assert result.status == DeploymentRequestStatus.FAILED
    assert result.started_at is not None
    assert result.completed_at is not None
    assert result.error_message == (
        "Simulated infrastructure failure."
    )

    db_session.refresh(environment)

    assert environment.status == EnvironmentStatus.FAILED


def test_process_next_request_handles_unexpected_failure(
    db_session: Session,
    test_user: User,
) -> None:
    environment = create_environment_model(
        db_session,
        test_user,
        name="unexpected-failure-environment",
    )

    deployment_request = create_deployment_request_model(
        db_session,
        test_user,
        environment,
        operation=DeploymentOperation.PROVISION,
    )

    result = DeploymentWorkerService(
        db_session,
        executor=UnexpectedFailingExecutor(),
    ).process_next_request()

    assert result is not None
    assert result.id == deployment_request.id
    assert result.status == DeploymentRequestStatus.FAILED
    assert result.error_message == (
        "Unexpected deployment execution failure: "
        "Unexpected executor failure."
    )

    db_session.refresh(environment)

    assert environment.status == EnvironmentStatus.FAILED


def test_execute_request_rejects_non_processing_request(
    db_session: Session,
    test_user: User,
) -> None:
    environment = create_environment_model(
        db_session,
        test_user,
        name="invalid-state-environment",
    )

    deployment_request = create_deployment_request_model(
        db_session,
        test_user,
        environment,
        operation=DeploymentOperation.PROVISION,
        status=DeploymentRequestStatus.QUEUED,
    )

    worker = DeploymentWorkerService(
        db_session,
        executor=SuccessfulExecutor(),
    )

    with pytest.raises(
        ValueError,
        match="Only processing deployment requests may be executed",
    ):
        worker.execute_request(deployment_request)