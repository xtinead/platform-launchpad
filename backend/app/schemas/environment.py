import re
import uuid
from datetime import datetime
from typing import Any

from pydantic import Field, field_validator, model_validator

from app.models.enums import EnvironmentStatus, EnvironmentType
from app.schemas.common import APIModel, PaginatedResponse
from app.schemas.deployment_request import DeploymentRequestResponse


ENVIRONMENT_NAME_PATTERN = re.compile(
    r"^[a-z0-9][a-z0-9-]*[a-z0-9]$"
)


class EnvironmentCreateRequest(APIModel):
    name: str = Field(min_length=3, max_length=100)
    environment_type: EnvironmentType
    application_version: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=1000)

    @field_validator("name")
    @classmethod
    def validate_environment_name(cls, value: str) -> str:
        normalized_value = value.strip().lower()

        if not ENVIRONMENT_NAME_PATTERN.fullmatch(normalized_value):
            raise ValueError(
                "Environment name must use lowercase letters, numbers, "
                "and hyphens, and must begin and end with a letter or number."
            )

        return normalized_value

class EnvironmentUpdateRequest(APIModel):
    """Fields that an environment owner may update."""

    application_version: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )
    description: str | None = Field(
        default=None,
        max_length=1000,
    )

    @field_validator("application_version")
    @classmethod
    def normalize_application_version(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        normalized_value = value.strip()

        if not normalized_value:
            raise ValueError(
                "Application version must not be empty."
            )

        return normalized_value

    @field_validator("description")
    @classmethod
    def normalize_description(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        normalized_value = value.strip()

        return normalized_value or None

    @model_validator(mode="after")
    def require_at_least_one_field(
        self,
    ) -> "EnvironmentUpdateRequest":
        if not self.model_fields_set:
            raise ValueError(
                "At least one environment field must be provided."
            )

        return self

class EnvironmentResponse(APIModel):
    id: uuid.UUID
    owner_id: uuid.UUID
    name: str
    environment_type: EnvironmentType
    application_version: str
    description: str | None = None
    status: EnvironmentStatus
    external_url: str | None = None

    metadata: dict[str, Any] = Field(
        default_factory=dict,
        validation_alias="platform_metadata",
        serialization_alias="metadata",
    )

    created_at: datetime
    updated_at: datetime
    destroyed_at: datetime | None = None


class EnvironmentListResponse(
    PaginatedResponse[EnvironmentResponse]
):
    pass


class EnvironmentOperationResponse(APIModel):
    environment: EnvironmentResponse
    deployment_request: DeploymentRequestResponse