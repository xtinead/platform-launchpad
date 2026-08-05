import math
import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import (
    ActiveDeploymentRequestExistsError,
    DeploymentRequestAccessDeniedError,
    DeploymentRequestNotFoundError,
    EnvironmentAccessDeniedError,
    EnvironmentNotFoundError,
    InvalidDeploymentOperationError,
)
from app.models.deployment_request import DeploymentRequest
from app.models.enums import (
    DeploymentOperation,
    DeploymentRequestStatus,
    EnvironmentStatus,
    UserRole,
)
from app.models.user import User
from app.repositories.deployment_request_repository import (
    DeploymentRequestRepository,
)
from app.repositories.environment_repository import (
    EnvironmentRepository,
)
from app.schemas.common import PaginationMetadata
from app.schemas.deployment_request import (
    DeploymentRequestCreateRequest,
    DeploymentRequestListResponse,
    DeploymentRequestResponse,
)
from app.schemas.environment import EnvironmentOperationResponse


ALLOWED_OPERATIONS_BY_STATUS: dict[
    EnvironmentStatus,
    set[DeploymentOperation],
] = {
    EnvironmentStatus.PENDING: {
        DeploymentOperation.PROVISION,
        DeploymentOperation.DESTROY,
    },
    EnvironmentStatus.PROVISIONING: set(),
    EnvironmentStatus.ACTIVE: {
        DeploymentOperation.UPGRADE,
        DeploymentOperation.DESTROY,
    },
    EnvironmentStatus.FAILED: {
        DeploymentOperation.RETRY,
        DeploymentOperation.DESTROY,
    },
    EnvironmentStatus.DESTROYING: set(),
    EnvironmentStatus.DESTROYED: set(),
}


class DeploymentRequestService:
    """Business logic for asynchronous environment operations."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self.environments = EnvironmentRepository(session)
        self.deployment_requests = DeploymentRequestRepository(session)

    def create_request(
        self,
        *,
        current_user: User,
        environment_id: uuid.UUID,
        request: DeploymentRequestCreateRequest,
    ) -> EnvironmentOperationResponse:
        """Queue a lifecycle operation for an environment."""

        environment = self.environments.get_by_id(environment_id)

        if environment is None:
            raise EnvironmentNotFoundError()

        is_owner = environment.owner_id == current_user.id
        is_admin = current_user.role == UserRole.ADMIN

        if not is_owner and not is_admin:
            raise EnvironmentAccessDeniedError()

        environment_status = EnvironmentStatus(environment.status)

        allowed_operations = ALLOWED_OPERATIONS_BY_STATUS[
            environment_status
        ]

        if request.operation not in allowed_operations:
            raise InvalidDeploymentOperationError()

        if self.deployment_requests.has_active_for_environment(
            environment_id=environment.id,
        ):
            raise ActiveDeploymentRequestExistsError()

        deployment_request = DeploymentRequest(
            environment_id=environment.id,
            requested_by_id=current_user.id,
            operation=request.operation,
            status=DeploymentRequestStatus.QUEUED,
            attempt_count=0,
            request_payload=request.request_payload,
        )

        try:
            self.deployment_requests.add(deployment_request)
            self.session.commit()
            self.session.refresh(environment)
            self.session.refresh(deployment_request)
        except Exception:
            self.session.rollback()
            raise

        return EnvironmentOperationResponse(
            environment=environment,
            deployment_request=DeploymentRequestResponse.model_validate(
                deployment_request
            ),
        )

    def list_requests(
        self,
        *,
        current_user: User,
        page: int,
        page_size: int,
        status: DeploymentRequestStatus | None = None,
        operation: DeploymentOperation | None = None,
    ) -> DeploymentRequestListResponse:
        """Return deployment requests visible to the current user."""

        offset = (page - 1) * page_size

        deployment_requests = self.deployment_requests.list_for_owner(
            owner_id=current_user.id,
            offset=offset,
            limit=page_size,
            status=status,
            operation=operation,
        )

        total = self.deployment_requests.count_for_owner(
            owner_id=current_user.id,
            status=status,
            operation=operation,
        )

        total_pages = math.ceil(total / page_size) if total > 0 else 0

        return DeploymentRequestListResponse(
            items=[
                DeploymentRequestResponse.model_validate(
                    deployment_request
                )
                for deployment_request in deployment_requests
            ],
            pagination=PaginationMetadata(
                page=page,
                page_size=page_size,
                total_items=total,
                total_pages=total_pages,
            ),
        )

    def get_request(
        self,
        *,
        current_user: User,
        deployment_request_id: uuid.UUID,
    ) -> DeploymentRequestResponse:
        """Return a deployment request visible to the current user."""

        deployment_request = self.deployment_requests.get_by_id(
            deployment_request_id
        )

        if deployment_request is None:
            raise DeploymentRequestNotFoundError()

        environment = self.environments.get_by_id(
            deployment_request.environment_id
        )

        if environment is None:
            raise EnvironmentNotFoundError()

        is_owner = environment.owner_id == current_user.id
        is_admin = current_user.role == UserRole.ADMIN

        if not is_owner and not is_admin:
            raise DeploymentRequestAccessDeniedError()

        return DeploymentRequestResponse.model_validate(
            deployment_request
        )