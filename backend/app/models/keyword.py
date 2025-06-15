"""
Keyword model for tagging and categorizing notes
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.note import note_keywords


class Keyword(Base):
    """Keyword model for tagging and categorizing notes."""
    
    __tablename__ = "keywords"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Keyword information
    name = Column(String, nullable=False, index=True)
    
    # User ownership
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    owner = relationship("User", back_populates="keywords")
    notes = relationship("Note", secondary=note_keywords, back_populates="keywords")
    
    def __repr__(self):
        return f"<Keyword(name='{self.name}', owner='{self.user_id}')>"