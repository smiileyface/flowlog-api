from uuid import UUID

from .base import BaseSchema, IDMixin, TimestampMixin


class NoteBase(BaseSchema):
    """Base note fields shared across operations."""

    text: str
    meta: dict | None = None


class NoteCreate(NoteBase):
    """Schema for creating a new note (POST)."""

    journal_id: UUID | None = None


class NoteUpdate(NoteBase):
    """Schema for updating a note (PUT) - full replacement."""

    journal_id: UUID | None = None


class NoteRead(NoteBase, IDMixin, TimestampMixin):
    """Schema for reading a note (GET) - includes ID and timestamps."""

    journal_id: UUID | None = None
    # tags relationship will be populated separately if needed
