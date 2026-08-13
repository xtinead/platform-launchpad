from dataclasses import dataclass
from typing import Any

from app.models.deployment_request import DeploymentRequest
from app.models.enums import DeploymentOperation


@dataclass(frozen=True)
class DeploymentExecutionResult:
    """Result returned by an infrastructure deployment executor."""

    metadata: dict[str, Any]


class DeploymentExecutionError(RuntimeError):
    """Raised when an infrastructure operation cannot be completed."""


class DeploymentExecutor:
    """
    Execute infrastructure operations requested by the platform worker.

    This initial implementation is deterministic and simulates successful
    infrastructure execution. It can later be replaced by Jenkins,
    Terraform, Kubernetes, or cloud-provider integrations.
    """

    def execute(
        self,
        deployment_request: DeploymentRequest,
    ) -> DeploymentExecutionResult:
        """Dispatch the deployment request to the matching operation."""

        operation = DeploymentOperation(
            deployment_request.operation
        )

        handlers = {
            DeploymentOperation.PROVISION: self.provision,
            DeploymentOperation.DESTROY: self.destroy,
            DeploymentOperation.RETRY: self.retry,
            DeploymentOperation.UPGRADE: self.upgrade,
        }

        handler = handlers.get(operation)

        if handler is None:
            raise DeploymentExecutionError(
                f"Unsupported deployment operation: {operation}"
            )

        return handler(deployment_request)

    def provision(
        self,
        deployment_request: DeploymentRequest,
    ) -> DeploymentExecutionResult:
        """Simulate provisioning an environment."""

        return DeploymentExecutionResult(
            metadata={
                "executor": "simulated",
                "operation": "provision",
                "deployment_request_id": str(
                    deployment_request.id
                ),
            },
        )

    def destroy(
        self,
        deployment_request: DeploymentRequest,
    ) -> DeploymentExecutionResult:
        """Simulate destroying an environment."""

        return DeploymentExecutionResult(
            metadata={
                "executor": "simulated",
                "operation": "destroy",
                "deployment_request_id": str(
                    deployment_request.id
                ),
            },
        )

    def retry(
        self,
        deployment_request: DeploymentRequest,
    ) -> DeploymentExecutionResult:
        """Simulate retrying a failed environment deployment."""

        return DeploymentExecutionResult(
            metadata={
                "executor": "simulated",
                "operation": "retry",
                "deployment_request_id": str(
                    deployment_request.id
                ),
            },
        )

    def upgrade(
        self,
        deployment_request: DeploymentRequest,
    ) -> DeploymentExecutionResult:
        """Simulate upgrading an active environment."""

        return DeploymentExecutionResult(
            metadata={
                "executor": "simulated",
                "operation": "upgrade",
                "deployment_request_id": str(
                    deployment_request.id
                ),
            },
        )