import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import CheckConstraint, ForeignKey, Index, Integer, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import DeploymentOperation, DeploymentRequestStatus
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.audit_log import AuditLog
    from app.models.environment import Environment
    from app.models.user import User


class DeploymentRequest(TimestampMixin, Base):
    """Asynchronous lifecycle operation for an environment."""

    __tablename__ = "deployment_requests"
    __table_args__ = (
        CheckConstraint(
            "operation IN ('provision', 'destroy', 'retry', 'upgrade')",
            name="valid_operation",
        ),
        CheckConstraint(
            (
                "status IN "
                "('queued', 'processing', 'succeeded', 'failed', 'cancelled')"
            ),
            name="valid_status",
        ),
        CheckConstraint(
            "attempt_count >= 0",
            name="nonnegative_attempt_count",
        ),
        Index(
            "ix_deployment_requests_environment_id_status",
            "environment_id",
            "status",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    environment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("environments.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    requested_by_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    operation: Mapped[DeploymentOperation] = mapped_column(
        String(30),
        nullable=False,
        index=True,
    )

    status: Mapped[DeploymentRequestStatus] = mapped_column(
        String(20),
        nullable=False,
        default=DeploymentRequestStatus.QUEUED,
        server_default=text("'queued'"),
        index=True,
    )

    attempt_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default=text("0"),
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    request_payload: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default=text("'{}'::jsonb"),
    )

    requested_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        index=True,
    )

    started_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )

    environment: Mapped["Environment"] = relationship(
        back_populates="deployment_requests",
    )

    requested_by: Mapped["User"] = relationship(
        back_populates="deployment_requests",
    )

    audit_logs: Mapped[list["AuditLog"]] = relationship(
        back_populates="deployment_request",
    )