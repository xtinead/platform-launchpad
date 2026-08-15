import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import CheckConstraint, ForeignKey, Index, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import UniqueConstraint

from app.db.base import Base
from app.models.enums import EnvironmentStatus, EnvironmentType
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.audit_log import AuditLog
    from app.models.deployment_request import DeploymentRequest
    from app.models.user import User


class Environment(TimestampMixin, Base):
    """Developer-requested application environment."""

    __tablename__ = "environments"
    __table_args__ = (
        CheckConstraint(
            "environment_type IN ('development', 'staging', 'demo')",
            name="valid_environment_type",
        ),
        CheckConstraint(
            (
                "status IN "
                "('pending', 'provisioning', 'active', "
                "'failed', 'destroying', 'destroyed')"
            ),
            name="valid_status",
        ),
        Index(
            "ix_environments_owner_id_status",
            "owner_id",
            "status",
        ),
        Index(
            "ix_environments_owner_id_name",
            "owner_id",
            "name",
        ),
        UniqueConstraint(
            "owner_id",
            "name",
            name="uq_environments_owner_id_name",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    environment_type: Mapped[EnvironmentType] = mapped_column(
        String(20),
        nullable=False,
        index=True,
    )

    application_version: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    status: Mapped[EnvironmentStatus] = mapped_column(
        String(20),
        nullable=False,
        default=EnvironmentStatus.PENDING,
        server_default=text("'pending'"),
        index=True,
    )

    external_url: Mapped[str | None] = mapped_column(
        String(2048),
        nullable=True,
    )

    platform_metadata: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSONB,
        nullable=False,
        default=dict,
        server_default=text("'{}'::jsonb"),
    )

    destroyed_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )

    owner: Mapped["User"] = relationship(
        back_populates="environments",
    )

    deployment_requests: Mapped[list["DeploymentRequest"]] = relationship(
        back_populates="environment",
    )

    audit_logs: Mapped[list["AuditLog"]] = relationship(
        back_populates="environment",
    )