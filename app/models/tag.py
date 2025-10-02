from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from .base import BaseModel
from .note import note_tags


class Tag(BaseModel):
    __tablename__ = "tags"

    name = Column(String(50), unique=True, nullable=False)

    # Relationships
    notes = relationship("Note", secondary=note_tags, back_populates="tags")
