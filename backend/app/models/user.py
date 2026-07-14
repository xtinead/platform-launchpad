import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, CheckConstraint, DateTime, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import UserRole
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.audit_log import AuditLog
    from app.models.deployment_request import DeploymentRequest
    from app.models.environment import Environment


class User(TimestampMixin, Base):
    """Application user identity."""

    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint(
            "role IN ('user', 'admin')",
            name="valid_role",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    email: Mapped[str] = mapped_column(
        String(320),
        nullable=False,
        unique=True,
        index=True,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    full_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    role: Mapped[UserRole] = mapped_column(
        String(20),
        nullable=False,
        default=UserRole.USER,
        server_default=text("'user'"),
        index=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=text("true"),
        index=True,
    )

    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    environments: Mapped[list["Environment"]] = relationship(
        back_populates="owner",
    )

    deployment_requests: Mapped[list["DeploymentRequest"]] = relationship(
        back_populates="requested_by",
    )

    audit_logs: Mapped[list["AuditLog"]] = relationship(
        back_populates="user",
    )