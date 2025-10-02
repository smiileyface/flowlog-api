from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """Base schema with common Pydantic configuration."""

    model_config = ConfigDict(from_attributes=True)


# Mixins - composable schema components
class IDMixin(BaseModel):
    """Mixin for ID field."""

    id: UUID


class TimestampMixin(BaseModel):
    """Mixin for timestamp fields."""

    created_at: datetime
    updated_at: datetime


class SoftDeleteMixin(BaseModel):
    """Mixin for soft delete functionality."""

    deleted_at: datetime | None = None
    is_deleted: bool = False


class AuditMixin(BaseModel):
    """Mixin for audit trail fields."""

    created_by: UUID | None = None
    updated_by: UUID | None = None


# Common combinations
class ReadSchema(BaseSchema, IDMixin, TimestampMixin):
    """Standard read schema with ID and timestamps."""

    pass


class AuditedReadSchema(BaseSchema, IDMixin, TimestampMixin, AuditMixin):
    """Read schema with audit trail."""

    pass
