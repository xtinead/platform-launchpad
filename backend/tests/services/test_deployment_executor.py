import uuid

import pytest

from app.models.deployment_request import DeploymentRequest
from app.models.enums import DeploymentOperation
from app.services.deployment_executor import (
    DeploymentExecutionResult,
    DeploymentExecutor,
)


def deployment_request_for(
    operation: DeploymentOperation,
) -> DeploymentRequest:
    """Create an in-memory deployment request for executor tests."""

    return DeploymentRequest(
        id=uuid.uuid4(),
        environment_id=uuid.uuid4(),
        requested_by_id=uuid.uuid4(),
        operation=operation,
        request_payload={},
    )


@pytest.mark.parametrize(
    ("operation", "expected_operation"),
    [
        (DeploymentOperation.PROVISION, "provision"),
        (DeploymentOperation.DESTROY, "destroy"),
        (DeploymentOperation.RETRY, "retry"),
        (DeploymentOperation.UPGRADE, "upgrade"),
    ],
)
def test_executor_dispatches_supported_operations(
    operation: DeploymentOperation,
    expected_operation: str,
) -> None:
    deployment_request = deployment_request_for(operation)

    result = DeploymentExecutor().execute(deployment_request)

    assert isinstance(result, DeploymentExecutionResult)
    assert result.metadata == {
        "executor": "simulated",
        "operation": expected_operation,
        "deployment_request_id": str(deployment_request.id),
    }


def test_provision_returns_simulated_metadata() -> None:
    deployment_request = deployment_request_for(
        DeploymentOperation.PROVISION
    )

    result = DeploymentExecutor().provision(deployment_request)

    assert result.metadata["executor"] == "simulated"
    assert result.metadata["operation"] == "provision"


def test_destroy_returns_simulated_metadata() -> None:
    deployment_request = deployment_request_for(
        DeploymentOperation.DESTROY
    )

    result = DeploymentExecutor().destroy(deployment_request)

    assert result.metadata["executor"] == "simulated"
    assert result.metadata["operation"] == "destroy"


def test_retry_returns_simulated_metadata() -> None:
    deployment_request = deployment_request_for(
        DeploymentOperation.RETRY
    )

    result = DeploymentExecutor().retry(deployment_request)

    assert result.metadata["executor"] == "simulated"
    assert result.metadata["operation"] == "retry"


def test_upgrade_returns_simulated_metadata() -> None:
    deployment_request = deployment_request_for(
        DeploymentOperation.UPGRADE
    )

    result = DeploymentExecutor().upgrade(deployment_request)

    assert result.metadata["executor"] == "simulated"
    assert result.metadata["operation"] == "upgrade"