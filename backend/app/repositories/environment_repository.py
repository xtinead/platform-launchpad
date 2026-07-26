import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.environment import Environment
from app.models.enums import EnvironmentStatus


class EnvironmentRepository:
    """Data-access operations for application environments."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(
        self,
        environment_id: uuid.UUID,
    ) -> Environment | None:
        """Return an environment by its primary key."""

        statement = select(Environment).where(
            Environment.id == environment_id,
        )

        return self.session.scalar(statement)

    def get_by_owner_and_name(
        self,
        *,
        owner_id: uuid.UUID,
        name: str,
    ) -> Environment | None:
        """Return an owner's environment with the supplied name."""

        normalized_name = name.strip().lower()

        statement = select(Environment).where(
            Environment.owner_id == owner_id,
            Environment.name == normalized_name,
        )

        return self.session.scalar(statement)

    def list_for_owner(
        self,
        *,
        owner_id: uuid.UUID,
        offset: int = 0,
        limit: int = 20,
        status: EnvironmentStatus | None = None,
    ) -> list[Environment]:
        """Return a paginated collection of environments for an owner."""

        statement = (
            select(Environment)
            .where(Environment.owner_id == owner_id)
            .order_by(Environment.created_at.desc())
            .offset(offset)
            .limit(limit)
        )

        if status is not None:
            statement = statement.where(
                Environment.status == status,
            )

        return list(self.session.scalars(statement).all())

    def count_for_owner(
        self,
        *,
        owner_id: uuid.UUID,
        status: EnvironmentStatus | None = None,
    ) -> int:
        """Count environments belonging to an owner."""

        statement = (
            select(func.count())
            .select_from(Environment)
            .where(Environment.owner_id == owner_id)
        )

        if status is not None:
            statement = statement.where(
                Environment.status == status,
            )

        return int(self.session.scalar(statement) or 0)

    def add(
        self,
        environment: Environment,
    ) -> Environment:
        """Add and flush an environment."""

        self.session.add(environment)
        self.session.flush()
        self.session.refresh(environment)

        return environment