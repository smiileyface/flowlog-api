from .base import BaseSchema, IDMixin, TimestampMixin


class TagBase(BaseSchema):
    """Base tag fields shared across operations."""

    name: str


class TagCreate(TagBase):
    """Schema for creating a new tag (POST)."""

    pass


class TagUpdate(TagBase):
    """Schema for updating a tag (PUT) - full replacement."""

    pass


class TagRead(TagBase, IDMixin, TimestampMixin):
    """Schema for reading a tag (GET) - includes ID and timestamps."""

    pass
    # notes relationship will be populated separately if needed
