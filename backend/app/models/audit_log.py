import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import CheckConstraint, ForeignKey, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import AuditResult

if TYPE_CHECKING:
    from app.models.deployment_request import DeploymentRequest
    from app.models.environment import Environment
    from app.models.user import User


class AuditLog(Base):
    """Immutable security and operational event."""

    __tablename__ = "audit_logs"
    __table_args__ = (
        CheckConstraint(
            "result IN ('success', 'failure', 'denied')",
            name="valid_result",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    environment_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("environments.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    deployment_request_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("deployment_requests.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    action: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    resource_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    resource_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )

    result: Mapped[AuditResult] = mapped_column(
        String(20),
        nullable=False,
        default=AuditResult.SUCCESS,
        server_default=text("'success'"),
        index=True,
    )

    message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    details: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default=text("'{}'::jsonb"),
    )

    source_ip: Mapped[str | None] = mapped_column(
        String(45),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        index=True,
    )

    user: Mapped["User | None"] = relationship(
        back_populates="audit_logs",
    )

    environment: Mapped["Environment | None"] = relationship(
        back_populates="audit_logs",
    )

    deployment_request: Mapped["DeploymentRequest | None"] = relationship(
        back_populates="audit_logs",
    )