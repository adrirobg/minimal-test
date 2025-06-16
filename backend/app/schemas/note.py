"""
Note Pydantic schemas for validation and serialization
"""
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, field_validator


class NoteBase(BaseModel):
    """Base Note schema with common fields."""
    title: Optional[str] = None
    content: str
    note_type: Optional[str] = "text"
    note_metadata: Optional[Dict[str, Any]] = None
    project_id: Optional[uuid.UUID] = None
    source_id: Optional[uuid.UUID] = None
    
    @field_validator('content')
    @classmethod
    def validate_content(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Note content cannot be empty')
        if len(v.strip()) > 100000:  # 100KB limit
            raise ValueError('Note content cannot exceed 100,000 characters')
        return v.strip()
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if len(v.strip()) > 500:
            raise ValueError('Note title cannot exceed 500 characters')
        return v.strip() if v.strip() else None
    
    @field_validator('note_type')
    @classmethod
    def validate_note_type(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return "text"
        allowed_types = ["text", "markdown", "task", "idea", "reference", "summary", "question"]
        if v not in allowed_types:
            raise ValueError(f'Note type must be one of: {", ".join(allowed_types)}')
        return v


class NoteCreate(NoteBase):
    """Schema for creating a new note."""
    keyword_ids: Optional[List[uuid.UUID]] = []


class NoteUpdate(BaseModel):
    """Schema for updating note information."""
    title: Optional[str] = None
    content: Optional[str] = None
    note_type: Optional[str] = None
    note_metadata: Optional[Dict[str, Any]] = None
    project_id: Optional[uuid.UUID] = None
    source_id: Optional[uuid.UUID] = None
    keyword_ids: Optional[List[uuid.UUID]] = None
    
    @field_validator('content')
    @classmethod
    def validate_content(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not v or not v.strip():
            raise ValueError('Note content cannot be empty')
        if len(v.strip()) > 100000:
            raise ValueError('Note content cannot exceed 100,000 characters')
        return v.strip()
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if len(v.strip()) > 500:
            raise ValueError('Note title cannot exceed 500 characters')
        return v.strip() if v.strip() else None


class NoteInDB(NoteBase):
    """Schema for note data as stored in database."""
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class NoteResponse(NoteBase):
    """Schema for note data in API responses."""
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class NoteWithKeywords(NoteResponse):
    """Schema for note with associated keywords."""
    keywords: List['KeywordResponse'] = []
    
    class Config:
        from_attributes = True


class NoteWithProject(NoteResponse):
    """Schema for note with project information."""
    project_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class NoteWithSource(NoteResponse):
    """Schema for note with source information."""
    source_name: Optional[str] = None
    source_type: Optional[str] = None
    
    class Config:
        from_attributes = True


class NoteDetail(NoteResponse):
    """Schema for detailed note information."""
    keywords: List['KeywordResponse'] = []
    project_name: Optional[str] = None
    source_name: Optional[str] = None
    outgoing_links_count: int = 0
    incoming_links_count: int = 0
    
    class Config:
        from_attributes = True


class NoteSearch(BaseModel):
    """Schema for note search parameters."""
    query: Optional[str] = None
    project_id: Optional[uuid.UUID] = None
    source_id: Optional[uuid.UUID] = None
    note_type: Optional[str] = None
    keyword_ids: Optional[List[uuid.UUID]] = []
    limit: int = 20
    offset: int = 0
    
    @field_validator('limit')
    @classmethod
    def validate_limit(cls, v: int) -> int:
        if v < 1 or v > 100:
            raise ValueError('Limit must be between 1 and 100')
        return v


# Import here to avoid circular imports
from .keyword import KeywordResponse
NoteWithKeywords.model_rebuild()
NoteDetail.model_rebuild()