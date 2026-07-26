import math
import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import (
    EnvironmentAccessDeniedError,
    EnvironmentNameAlreadyExistsError,
    EnvironmentNotFoundError,
    InvalidEnvironmentOperationError,
)
from app.models.environment import Environment
from app.models.enums import EnvironmentStatus, UserRole
from app.models.user import User
from app.repositories.environment_repository import EnvironmentRepository
from app.schemas.common import PaginationMetadata
from app.schemas.environment import (
    EnvironmentCreateRequest,
    EnvironmentListResponse,
    EnvironmentResponse,
    EnvironmentUpdateRequest,
)


class EnvironmentService:
    """Business logic for developer-managed environments."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self.environments = EnvironmentRepository(session)

    def create_environment(
        self,
        *,
        current_user: User,
        request: EnvironmentCreateRequest,
    ) -> EnvironmentResponse:
        """Create a pending environment owned by the current user."""

        existing_environment = (
            self.environments.get_by_owner_and_name(
                owner_id=current_user.id,
                name=request.name,
            )
        )

        if existing_environment is not None:
            raise EnvironmentNameAlreadyExistsError()

        environment = Environment(
            owner_id=current_user.id,
            name=request.name,
            environment_type=request.environment_type,
            application_version=request.application_version,
            description=request.description,
            status=EnvironmentStatus.PENDING,
            platform_metadata={},
        )

        try:
            self.environments.add(environment)
            self.session.commit()
            self.session.refresh(environment)
        except IntegrityError as exc:
            self.session.rollback()
            raise EnvironmentNameAlreadyExistsError() from exc
        except Exception:
            self.session.rollback()
            raise

        return EnvironmentResponse.model_validate(environment)

    def get_environment(
        self,
        *,
        current_user: User,
        environment_id: uuid.UUID,
    ) -> EnvironmentResponse:
        """Return an environment visible to the current user."""

        environment = self._get_accessible_environment(
            current_user=current_user,
            environment_id=environment_id,
        )

        return EnvironmentResponse.model_validate(environment)

    def list_environments(
        self,
        *,
        current_user: User,
        page: int,
        page_size: int,
        status: EnvironmentStatus | None = None,
    ) -> EnvironmentListResponse:
        """Return paginated environments owned by the current user."""

        offset = (page - 1) * page_size

        environments = self.environments.list_for_owner(
            owner_id=current_user.id,
            offset=offset,
            limit=page_size,
            status=status,
        )

        total = self.environments.count_for_owner(
            owner_id=current_user.id,
            status=status,
        )

        total_pages = math.ceil(total / page_size) if total > 0 else 0

        return EnvironmentListResponse(
            items=[
                EnvironmentResponse.model_validate(environment)
                for environment in environments
            ],
            pagination=PaginationMetadata(
                page=page,
                page_size=page_size,
                total_items=total,
                total_pages=total_pages,
            ),
        )

    def update_environment(
        self,
        *,
        current_user: User,
        environment_id: uuid.UUID,
        request: EnvironmentUpdateRequest,
    ) -> EnvironmentResponse:
        """Update editable environment fields."""

        environment = self._get_accessible_environment(
            current_user=current_user,
            environment_id=environment_id,
        )

        editable_statuses = {
            EnvironmentStatus.PENDING,
            EnvironmentStatus.ACTIVE,
            EnvironmentStatus.FAILED,
        }

        if environment.status not in editable_statuses:
            raise InvalidEnvironmentOperationError()

        update_fields = request.model_dump(
            exclude_unset=True,
        )

        if "application_version" in update_fields:
            environment.application_version = (
                request.application_version
            )

        if "description" in update_fields:
            environment.description = request.description

        try:
            self.session.commit()
            self.session.refresh(environment)
        except Exception:
            self.session.rollback()
            raise

        return EnvironmentResponse.model_validate(environment)

    def _get_accessible_environment(
        self,
        *,
        current_user: User,
        environment_id: uuid.UUID,
    ) -> Environment:
        """Resolve an environment and enforce ownership access."""

        environment = self.environments.get_by_id(environment_id)

        if environment is None:
            raise EnvironmentNotFoundError()

        is_owner = environment.owner_id == current_user.id
        is_admin = current_user.role == UserRole.ADMIN

        if not is_owner and not is_admin:
            raise EnvironmentAccessDeniedError()

        return environment