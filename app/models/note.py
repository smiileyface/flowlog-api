from sqlalchemy import Table, Column, ForeignKey, Text, MetaData
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from .base import BaseModel, Base

# Association table for many-to-many relationship between notes and tags
note_tags = Table(
    "note_tags",
    Base.metadata,
    Column("note_id", UUID(as_uuid=True), ForeignKey("notes.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", UUID(as_uuid=True), ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class Note(BaseModel):
    __tablename__ = "notes"

    text = Column(Text, nullable=False)
    meta = Column(JSONB, nullable=True)

    # Foreign keys
    journal_id = Column(UUID(as_uuid=True), ForeignKey("journals.id"), nullable=True)

    # Relationships
    journal = relationship("Journal", back_populates="notes")
    tags = relationship("Tag", secondary=note_tags, back_populates="notes")

