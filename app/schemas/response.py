from typing import Any, TypeVar

from pydantic import BaseModel, Field

# Generic type variable for response data
T = TypeVar("T")


class HealthResponse(BaseModel):
    status: str
    app: str
    version: str
    environment: str


class RootResponse(BaseModel):
    message: str
    version: str
    docs: str
    redoc: str
    health: str


class ErrorResponse(BaseModel):
    """
    Standardized error response model.
    """

    error: str
    message: str
    status_code: int
    path: str | None = None
    request_id: str | None = None
    details: Any | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "error": "Not Found",
                "message": "The requested resource was not found",
                "status_code": 404,
                "path": "/api/v1/journals/999",
                "request_id": "17278104",
                "details": None,
            }
        }


class DataResponse[T](BaseModel):
    """
    Generic single object response.

    Example:
        DataResponse[JournalSchema](
            success=True,
            message="Journal retrieved successfully",
            data=journal
        )
    """

    success: bool = True
    message: str
    data: T

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Resource retrieved successfully",
                "data": {"id": 1, "title": "Example"},
            }
        }


class ListResponse[T](BaseModel):
    """
    Generic list response without pagination.

    Example:
        ListResponse[JournalSchema](
            success=True,
            message="Journals retrieved successfully",
            data=[journal1, journal2],
            count=2
        )
    """

    success: bool = True
    message: str
    data: list[T]
    count: int

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Resources retrieved successfully",
                "data": [
                    {"id": 1, "title": "Example 1"},
                    {"id": 2, "title": "Example 2"},
                ],
                "count": 2,
            }
        }


class PaginationMeta(BaseModel):
    """
    Pagination metadata.
    """

    page: int = Field(..., ge=1, description="Current page number")
    per_page: int = Field(..., ge=1, le=100, description="Items per page")
    total: int = Field(..., ge=0, description="Total number of items")
    total_pages: int = Field(..., ge=0, description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_prev: bool = Field(..., description="Whether there is a previous page")

    class Config:
        json_schema_extra = {
            "example": {
                "page": 1,
                "per_page": 20,
                "total": 45,
                "total_pages": 3,
                "has_next": True,
                "has_prev": False,
            }
        }


class PaginatedResponse[T](BaseModel):
    """
    Generic paginated response.

    Example:
        PaginatedResponse[JournalSchema](
            success=True,
            message="Journals retrieved successfully",
            data=[journal1, journal2],
            pagination=PaginationMeta(...)
        )
    """

    success: bool = True
    message: str
    data: list[T]
    pagination: PaginationMeta

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Resources retrieved successfully",
                "data": [
                    {"id": 1, "title": "Example 1"},
                    {"id": 2, "title": "Example 2"},
                ],
                "pagination": {
                    "page": 1,
                    "per_page": 20,
                    "total": 45,
                    "total_pages": 3,
                    "has_next": True,
                    "has_prev": False,
                },
            }
        }


class MessageResponse(BaseModel):
    """
    Simple message response for operations that don't return data.

    Example:
        MessageResponse(
            success=True,
            message="Journal deleted successfully"
        )
    """

    success: bool = True
    message: str

    class Config:
        json_schema_extra = {
            "example": {"success": True, "message": "Operation completed successfully"}
        }
