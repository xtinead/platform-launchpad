from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field


class APIModel(BaseModel):
    """Base schema configuration shared by API models."""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        extra="forbid",
        str_strip_whitespace=True,
    )


class PaginationMetadata(APIModel):
    page: int = Field(ge=1)
    page_size: int = Field(ge=1, le=100)
    total_items: int = Field(ge=0)
    total_pages: int = Field(ge=0)


ItemType = TypeVar("ItemType")


class PaginatedResponse(APIModel, Generic[ItemType]):
    items: list[ItemType]
    pagination: PaginationMetadata


class ErrorDetail(APIModel):
    code: str
    message: str
    details: dict[str, Any] = Field(default_factory=dict)
    request_id: str


class ErrorResponse(APIModel):
    error: ErrorDetail