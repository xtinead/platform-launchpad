import uuid
# from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.deployment_request import DeploymentRequest
from app.models.environment import Environment
from app.models.enums import (
    DeploymentOperation,
    DeploymentRequestStatus,
)


ACTIVE_DEPLOYMENT_STATUSES = (
    DeploymentRequestStatus.QUEUED,
    DeploymentRequestStatus.PROCESSING,
)


class DeploymentRequestRepository:
    """Data-access operations for asynchronous deployment requests."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(
        self,
        deployment_request_id: uuid.UUID,
    ) -> DeploymentRequest | None:
        """Return a deployment request by its primary key."""

        statement = select(DeploymentRequest).where(
            DeploymentRequest.id == deployment_request_id,
        )

        return self.session.scalar(statement)

    def get_active_for_environment(
        self,
        *,
        environment_id: uuid.UUID,
    ) -> DeploymentRequest | None:
        """Return the current queued or processing request for an environment."""

        statement = (
            select(DeploymentRequest)
            .where(
                DeploymentRequest.environment_id == environment_id,
                DeploymentRequest.status.in_(
                    ACTIVE_DEPLOYMENT_STATUSES,
                ),
            )
            .order_by(DeploymentRequest.requested_at.desc())
            .limit(1)
        )

        return self.session.scalar(statement)

    def has_active_for_environment(
        self,
        *,
        environment_id: uuid.UUID,
    ) -> bool:
        """Return whether an environment has queued or processing work."""

        statement = (
            select(func.count())
            .select_from(DeploymentRequest)
            .where(
                DeploymentRequest.environment_id == environment_id,
                DeploymentRequest.status.in_(
                    ACTIVE_DEPLOYMENT_STATUSES,
                ),
            )
        )

        return bool(self.session.scalar(statement) or 0)

    def list_for_owner(
        self,
        *,
        owner_id: uuid.UUID,
        offset: int = 0,
        limit: int = 20,
        status: DeploymentRequestStatus | None = None,
        operation: DeploymentOperation | None = None,
    ) -> list[DeploymentRequest]:
        """Return deployment requests for environments owned by a user."""

        statement = (
            select(DeploymentRequest)
            .join(
                Environment,
                Environment.id == DeploymentRequest.environment_id,
            )
            .where(Environment.owner_id == owner_id)
            .order_by(DeploymentRequest.requested_at.desc())
            .offset(offset)
            .limit(limit)
        )

        if status is not None:
            statement = statement.where(
                DeploymentRequest.status == status,
            )

        if operation is not None:
            statement = statement.where(
                DeploymentRequest.operation == operation,
            )

        return list(self.session.scalars(statement).all())

    def count_for_owner(
        self,
        *,
        owner_id: uuid.UUID,
        status: DeploymentRequestStatus | None = None,
        operation: DeploymentOperation | None = None,
    ) -> int:
        """Count deployment requests for environments owned by a user."""

        statement = (
            select(func.count())
            .select_from(DeploymentRequest)
            .join(
                Environment,
                Environment.id == DeploymentRequest.environment_id,
            )
            .where(Environment.owner_id == owner_id)
        )

        if status is not None:
            statement = statement.where(
                DeploymentRequest.status == status,
            )

        if operation is not None:
            statement = statement.where(
                DeploymentRequest.operation == operation,
            )

        return int(self.session.scalar(statement) or 0)

    def list_for_environment(
        self,
        *,
        environment_id: uuid.UUID,
        offset: int = 0,
        limit: int = 20,
    ) -> list[DeploymentRequest]:
        """Return deployment history for one environment."""

        statement = (
            select(DeploymentRequest)
            .where(
                DeploymentRequest.environment_id == environment_id,
            )
            .order_by(DeploymentRequest.requested_at.desc())
            .offset(offset)
            .limit(limit)
        )

        return list(self.session.scalars(statement).all())

    def list_queued(
        self,
        *,
        limit: int = 20,
    ) -> list[DeploymentRequest]:
        """Return the oldest queued deployment requests for worker polling."""

        statement = (
            select(DeploymentRequest)
            .where(
                DeploymentRequest.status
                == DeploymentRequestStatus.QUEUED,
            )
            .order_by(DeploymentRequest.requested_at.asc())
            .limit(limit)
        )

        return list(self.session.scalars(statement).all())

    def add(
        self,
        deployment_request: DeploymentRequest,
    ) -> DeploymentRequest:
        """Add and flush a deployment request."""

        self.session.add(deployment_request)
        self.session.flush()
        self.session.refresh(deployment_request)

        return deployment_request