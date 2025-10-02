from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship

from .base import BaseModel


class Project(BaseModel):
    __tablename__ = "projects"

    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)

    # Relationships
    journals = relationship(
        "Journal", back_populates="project", cascade="all, delete-orphan"
    )
