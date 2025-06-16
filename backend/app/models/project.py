"""
Project model for hierarchical organization of notes
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base


class Project(Base):
    """Project model for organizing notes hierarchically."""
    
    __tablename__ = "projects"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Project information
    name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Hierarchical relationship (self-referencing)
    parent_project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True, index=True)
    
    # User ownership
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    owner = relationship("User", back_populates="projects")
    parent_project = relationship("Project", remote_side=[id], backref="child_projects")
    notes = relationship("Note", back_populates="project", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Project(name='{self.name}', owner='{self.user_id}')>"