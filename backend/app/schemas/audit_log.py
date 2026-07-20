import uuid
from datetime import datetime
from typing import Any

from app.models.enums import AuditResult
from app.schemas.common import APIModel, PaginatedResponse


class AuditLogResponse(APIModel):
    id: uuid.UUID
    user_id: uuid.UUID | None = None
    environment_id: uuid.UUID | None = None
    deployment_request_id: uuid.UUID | None = None
    action: str
    resource_type: str
    resource_id: uuid.UUID | None = None
    result: AuditResult
    message: str | None = None
    details: dict[str, Any]
    source_ip: str | None = None
    created_at: datetime


class AuditLogListResponse(PaginatedResponse[AuditLogResponse]):
    pass