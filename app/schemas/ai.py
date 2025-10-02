from uuid import UUID

from app.models.ai import AIJobStatus

from .base import BaseSchema, IDMixin, TimestampMixin


class AIJobBase(BaseSchema):
    """Base AIJob fields shared across operations."""

    journal_id: UUID
    model_name: str
    model_version: str | None = None
    prompt: str


class AIJobCreate(AIJobBase):
    """Schema for creating a new AI job (POST)."""

    pass


class AIJobUpdate(BaseSchema):
    """Schema for updating an AI job (PUT) - typically only status and response."""

    status: AIJobStatus | None = None
    response: dict | None = None
    error_message: str | None = None
    meta: dict | None = None


class AIJobRead(AIJobBase, IDMixin, TimestampMixin):
    """Schema for reading an AI job (GET) - includes ID, timestamps, and all fields."""

    status: AIJobStatus
    response: dict | None = None
    error_message: str | None = None
    meta: dict | None = None
