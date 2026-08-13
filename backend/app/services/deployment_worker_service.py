from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models.deployment_request import DeploymentRequest
from app.models.enums import (
    DeploymentOperation,
    DeploymentRequestStatus,
    EnvironmentStatus,
)
from app.repositories.deployment_request_repository import (
    DeploymentRequestRepository,
)
from app.repositories.environment_repository import (
    EnvironmentRepository,
)
from app.services.deployment_executor import (
    DeploymentExecutionError,
    DeploymentExecutionResult,
    DeploymentExecutor,
)


class DeploymentWorkerService:
    """Coordinate worker-side deployment lifecycle transitions."""

    def __init__(
        self,
        session: Session,
        executor: DeploymentExecutor | None = None,
    ) -> None:
        self.session = session
        self.deployment_requests = DeploymentRequestRepository(
            session
        )
        self.environments = EnvironmentRepository(session)
        self.executor = executor or DeploymentExecutor()

    def claim_next_request(
        self,
    ) -> DeploymentRequest | None:
        """
        Claim the oldest queued request and synchronize its environment.

        Request claiming and environment-state updates occur in the same
        database transaction.
        """

        try:
            deployment_request = (
                self.deployment_requests.claim_next_queued()
            )

            if deployment_request is None:
                self.session.rollback()
                return None

            environment = self.environments.get_by_id(
                deployment_request.environment_id
            )

            if environment is None:
                self.deployment_requests.mark_failed(
                    deployment_request,
                    error_message=(
                        "The deployment environment no longer exists."
                    ),
                )
                self.session.commit()
                self.session.refresh(deployment_request)
                return deployment_request

            operation = DeploymentOperation(
                deployment_request.operation
            )

            if operation == DeploymentOperation.DESTROY:
                environment.status = EnvironmentStatus.DESTROYING
            else:
                environment.status = EnvironmentStatus.PROVISIONING

            self.session.commit()
            self.session.refresh(deployment_request)

            return deployment_request

        except Exception:
            self.session.rollback()
            raise

    def execute_request(
        self,
        deployment_request: DeploymentRequest,
    ) -> DeploymentRequest:
        """
        Execute a previously claimed deployment request.

        Successful execution updates both the deployment request and its
        environment. Execution failures transition both resources to failed.
        """

        if (
            DeploymentRequestStatus(deployment_request.status)
            != DeploymentRequestStatus.PROCESSING
        ):
            raise ValueError(
                "Only processing deployment requests may be executed."
            )

        try:
            result = self.executor.execute(deployment_request)

            return self._complete_successfully(
                deployment_request=deployment_request,
                result=result,
            )

        except DeploymentExecutionError as exc:
            return self._complete_with_failure(
                deployment_request=deployment_request,
                error_message=str(exc),
            )
        except Exception as exc:
            return self._complete_with_failure(
                deployment_request=deployment_request,
                error_message=(
                    f"Unexpected deployment execution failure: {exc}"
                ),
            )

    def process_next_request(
        self,
    ) -> DeploymentRequest | None:
        """Claim and execute the next queued deployment request."""

        deployment_request = self.claim_next_request()

        if deployment_request is None:
            return None

        if (
            DeploymentRequestStatus(deployment_request.status)
            == DeploymentRequestStatus.FAILED
        ):
            return deployment_request

        return self.execute_request(deployment_request)

    def _complete_successfully(
        self,
        *,
        deployment_request: DeploymentRequest,
        result: DeploymentExecutionResult,
    ) -> DeploymentRequest:
        """Persist successful request and environment transitions."""

        try:
            environment = self.environments.get_by_id(
                deployment_request.environment_id
            )

            if environment is None:
                return self._complete_with_failure(
                    deployment_request=deployment_request,
                    error_message=(
                        "The deployment environment no longer exists."
                    ),
                )

            operation = DeploymentOperation(
                deployment_request.operation
            )

            if operation == DeploymentOperation.DESTROY:
                environment.status = EnvironmentStatus.DESTROYED
                environment.destroyed_at = datetime.now(UTC)
                environment.external_url = None
            else:
                environment.status = EnvironmentStatus.ACTIVE
                environment.destroyed_at = None

            environment.platform_metadata = {
                **(environment.platform_metadata or {}),
                **result.metadata,
            }

            self.deployment_requests.mark_succeeded(
                deployment_request
            )

            self.session.commit()
            self.session.refresh(environment)
            self.session.refresh(deployment_request)

            return deployment_request

        except Exception:
            self.session.rollback()
            raise

    def _complete_with_failure(
        self,
        *,
        deployment_request: DeploymentRequest,
        error_message: str,
    ) -> DeploymentRequest:
        """Persist failed request and environment transitions."""

        try:
            environment = self.environments.get_by_id(
                deployment_request.environment_id
            )

            if environment is not None:
                environment.status = EnvironmentStatus.FAILED

            self.deployment_requests.mark_failed(
                deployment_request,
                error_message=error_message,
            )

            self.session.commit()

            if environment is not None:
                self.session.refresh(environment)

            self.session.refresh(deployment_request)

            return deployment_request

        except Exception:
            self.session.rollback()
            raise