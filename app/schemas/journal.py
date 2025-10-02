from datetime import date
from uuid import UUID

from .base import BaseSchema, IDMixin, TimestampMixin


class JournalBase(BaseSchema):
    """Base journal fields shared across operations."""

    date: date


class JournalCreate(JournalBase):
    """Schema for creating a new journal (POST)."""

    project_id: UUID | None = None


class JournalUpdate(JournalBase):
    """Schema for updating a journal (PUT) - full replacement."""

    processed_markdown: str | None = None
    notes_snapshot: dict | None = None
    project_id: UUID | None = None


class JournalRead(JournalBase, IDMixin, TimestampMixin):
    """Schema for reading a journal (GET) - includes ID, timestamps, and all fields."""

    processed_markdown: str | None = None
    notes_snapshot: dict | None = None
    project_id: UUID | None = None
    # notes and ai_jobs relationships will be populated separately if needed
