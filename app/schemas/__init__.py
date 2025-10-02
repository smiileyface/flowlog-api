"""Schema exports for the application."""

from .ai import AIJobBase, AIJobCreate, AIJobRead, AIJobUpdate
from .base import (
    AuditedReadSchema,
    AuditMixin,
    BaseSchema,
    IDMixin,
    ReadSchema,
    SoftDeleteMixin,
    TimestampMixin,
)
from .journal import JournalBase, JournalCreate, JournalRead, JournalUpdate
from .note import NoteBase, NoteCreate, NoteRead, NoteUpdate
from .project import ProjectBase, ProjectCreate, ProjectRead, ProjectUpdate
from .response import (
    DataResponse,
    ErrorResponse,
    HealthResponse,
    ListResponse,
    MessageResponse,
    PaginatedResponse,
    PaginationMeta,
    RootResponse,
)
from .tag import TagBase, TagCreate, TagRead, TagUpdate

__all__ = [
    # Base schemas and mixins
    "BaseSchema",
    "IDMixin",
    "TimestampMixin",
    "SoftDeleteMixin",
    "AuditMixin",
    "ReadSchema",
    "AuditedReadSchema",
    # Response schemas
    "HealthResponse",
    "RootResponse",
    "ErrorResponse",
    "DataResponse",
    "ListResponse",
    "PaginatedResponse",
    "MessageResponse",
    "PaginationMeta",
    # Note schemas
    "NoteBase",
    "NoteCreate",
    "NoteUpdate",
    "NoteRead",
    # Journal schemas
    "JournalBase",
    "JournalCreate",
    "JournalUpdate",
    "JournalRead",
    # Project schemas
    "ProjectBase",
    "ProjectCreate",
    "ProjectUpdate",
    "ProjectRead",
    # Tag schemas
    "TagBase",
    "TagCreate",
    "TagUpdate",
    "TagRead",
    # AI Job schemas
    "AIJobBase",
    "AIJobCreate",
    "AIJobUpdate",
    "AIJobRead",
]
