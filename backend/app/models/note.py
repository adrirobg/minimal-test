"""
Note model - core content entity for PKM system
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Table, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base


# Association table for many-to-many relationship between notes and keywords
note_keywords = Table(
    'note_keywords',
    Base.metadata,
    Column('note_id', UUID(as_uuid=True), ForeignKey('notes.id'), primary_key=True),
    Column('keyword_id', UUID(as_uuid=True), ForeignKey('keywords.id'), primary_key=True)
)


class Note(Base):
    """Note model - core content entity for knowledge management."""
    
    __tablename__ = "notes"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Note content
    title = Column(String, nullable=True, index=True)
    content = Column(Text, nullable=False)
    note_type = Column(String, nullable=True)  # e.g., "text", "markdown", "task", etc.
    
    # Metadata stored as JSONB for flexibility (JSON for SQLite compatibility)
    note_metadata = Column(JSON, nullable=True)
    
    # Foreign keys
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True, index=True)
    source_id = Column(UUID(as_uuid=True), ForeignKey("sources.id"), nullable=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    owner = relationship("User", back_populates="notes")
    project = relationship("Project", back_populates="notes")
    source = relationship("Source", back_populates="notes")
    keywords = relationship("Keyword", secondary=note_keywords, back_populates="notes")
    
    # Note links (bidirectional relationships with other notes)
    outgoing_links = relationship(
        "NoteLink", 
        foreign_keys="NoteLink.source_note_id",
        back_populates="source_note",
        cascade="all, delete-orphan"
    )
    incoming_links = relationship(
        "NoteLink",
        foreign_keys="NoteLink.target_note_id", 
        back_populates="target_note",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<Note(title='{self.title}', owner='{self.user_id}')>"