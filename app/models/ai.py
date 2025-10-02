import enum

from sqlalchemy import Column, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from .base import BaseModel


class AIJobStatus(str, enum.Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    SUCCESS = "success"
    ERROR = "error"


class AIJob(BaseModel):
    __tablename__ = "ai_jobs"

    # Relations to journal
    journal_id = Column(UUID(as_uuid=True), ForeignKey("journals.id"), nullable=False)
    journal = relationship("Journal", back_populates="ai_jobs")

    # Model & prompt info
    model_name = Column(String, nullable=False)
    model_version = Column(String, nullable=True)
    prompt = Column(Text, nullable=False)
    response = Column(JSONB, nullable=True)

    # Status & errors
    status = Column(Enum(AIJobStatus), default=AIJobStatus.QUEUED, nullable=False)
    error_message = Column(Text, nullable=True)

    # Additional metadata
    meta = Column(JSONB, nullable=True)
