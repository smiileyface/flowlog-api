from sqlalchemy import Column, Date, ForeignKey, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from .base import BaseModel


class Journal(BaseModel):
    __tablename__ = "journals"

    date = Column(Date, nullable=False, unique=True)
    processed_markdown = Column(Text, nullable=True)
    notes_snapshot = Column(JSONB, nullable=True)

    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True)

    # Relationships
    project = relationship("Project", back_populates="journals")
    notes = relationship("Note", back_populates="journal", cascade="all, delete-orphan")
    ai_jobs = relationship(
        "AIJob", back_populates="journal", cascade="all, delete-orphan"
    )

    __table_args__ = (UniqueConstraint("date", name="uq_journal_date"),)
