"""
NoteLink model for bidirectional relationships between notes
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base


class NoteLink(Base):
    """NoteLink model for creating bidirectional relationships between notes."""
    
    __tablename__ = "note_links"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Link relationship
    source_note_id = Column(UUID(as_uuid=True), ForeignKey("notes.id"), nullable=False, index=True)
    target_note_id = Column(UUID(as_uuid=True), ForeignKey("notes.id"), nullable=False, index=True)
    
    # Link type for categorizing relationships
    link_type = Column(String, nullable=True)  # e.g., "reference", "related", "follow-up", etc.
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    source_note = relationship("Note", foreign_keys=[source_note_id], back_populates="outgoing_links")
    target_note = relationship("Note", foreign_keys=[target_note_id], back_populates="incoming_links")
    
    def __repr__(self):
        return f"<NoteLink(source='{self.source_note_id}', target='{self.target_note_id}', type='{self.link_type}')>"