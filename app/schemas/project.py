from .base import BaseSchema, IDMixin, TimestampMixin


class ProjectBase(BaseSchema):
    """Base project fields shared across operations."""

    name: str
    description: str | None = None


class ProjectCreate(ProjectBase):
    """Schema for creating a new project (POST)."""

    pass


class ProjectUpdate(ProjectBase):
    """Schema for updating a project (PUT) - full replacement."""

    pass


class ProjectRead(ProjectBase, IDMixin, TimestampMixin):
    """Schema for reading a project (GET) - includes ID and timestamps."""

    pass
    # journals relationship will be populated separately if needed
