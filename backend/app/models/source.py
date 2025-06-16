"""
Source model for external content sources
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base


class Source(Base):
    """Source model for managing external content sources."""
    
    __tablename__ = "sources"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Source information
    name = Column(String, nullable=False, index=True)
    source_type = Column(String, nullable=True)  # e.g., "web", "book", "pdf", "video", etc.
    
    # Source metadata stored as JSONB for flexibility (JSON for SQLite compatibility)
    # Can include: url, isbn, file_path, author, publication_date, etc.
    source_metadata = Column(JSON, nullable=True)
    
    # User ownership
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    owner = relationship("User", back_populates="sources")
    notes = relationship("Note", back_populates="source", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Source(name='{self.name}', type='{self.source_type}', owner='{self.user_id}')>"