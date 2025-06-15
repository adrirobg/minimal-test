"""
Source Pydantic schemas for validation and serialization
"""
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, field_validator, HttpUrl


class SourceBase(BaseModel):
    """Base Source schema with common fields."""
    name: str
    source_type: Optional[str] = "web"
    source_metadata: Optional[Dict[str, Any]] = None
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Source name cannot be empty')
        if len(v.strip()) < 2:
            raise ValueError('Source name must be at least 2 characters long')
        if len(v.strip()) > 300:
            raise ValueError('Source name cannot exceed 300 characters')
        return v.strip()
    
    @field_validator('source_type')
    @classmethod
    def validate_source_type(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return "web"
        allowed_types = [
            "web", "book", "pdf", "video", "podcast", "article", 
            "paper", "document", "image", "presentation", "other"
        ]
        if v.lower() not in allowed_types:
            raise ValueError(f'Source type must be one of: {", ".join(allowed_types)}')
        return v.lower()


class SourceCreate(SourceBase):
    """Schema for creating a new source."""
    pass


class SourceUpdate(BaseModel):
    """Schema for updating source information."""
    name: Optional[str] = None
    source_type: Optional[str] = None
    source_metadata: Optional[Dict[str, Any]] = None
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not v or not v.strip():
            raise ValueError('Source name cannot be empty')
        if len(v.strip()) < 2:
            raise ValueError('Source name must be at least 2 characters long')
        if len(v.strip()) > 300:
            raise ValueError('Source name cannot exceed 300 characters')
        return v.strip()
    
    @field_validator('source_type')
    @classmethod
    def validate_source_type(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        allowed_types = [
            "web", "book", "pdf", "video", "podcast", "article", 
            "paper", "document", "image", "presentation", "other"
        ]
        if v.lower() not in allowed_types:
            raise ValueError(f'Source type must be one of: {", ".join(allowed_types)}')
        return v.lower()


class SourceInDB(SourceBase):
    """Schema for source data as stored in database."""
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SourceResponse(SourceBase):
    """Schema for source data in API responses."""
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SourceWithNotes(SourceResponse):
    """Schema for source with associated notes count."""
    notes_count: int = 0
    
    class Config:
        from_attributes = True


class SourceDetail(SourceResponse):
    """Schema for detailed source information."""
    notes_count: int = 0
    recent_notes: List['NoteResponse'] = []
    
    class Config:
        from_attributes = True


class SourceSearch(BaseModel):
    """Schema for source search parameters."""
    query: Optional[str] = None
    source_type: Optional[str] = None
    limit: int = 20
    offset: int = 0
    include_notes: bool = False
    
    @field_validator('limit')
    @classmethod
    def validate_limit(cls, v: int) -> int:
        if v < 1 or v > 100:
            raise ValueError('Limit must be between 1 and 100')
        return v


class WebSourceCreate(SourceCreate):
    """Schema for creating a web source with URL validation."""
    url: HttpUrl
    
    def __init__(self, **data):
        if 'source_metadata' not in data:
            data['source_metadata'] = {}
        data['source_metadata']['url'] = str(data.get('url', ''))
        data['source_type'] = 'web'
        super().__init__(**data)


class BookSourceCreate(SourceCreate):
    """Schema for creating a book source with book-specific fields."""
    isbn: Optional[str] = None
    author: Optional[str] = None
    publication_year: Optional[int] = None
    
    def __init__(self, **data):
        if 'source_metadata' not in data:
            data['source_metadata'] = {}
        
        metadata = data['source_metadata']
        if 'isbn' in data:
            metadata['isbn'] = data.pop('isbn')
        if 'author' in data:
            metadata['author'] = data.pop('author')
        if 'publication_year' in data:
            metadata['publication_year'] = data.pop('publication_year')
        
        data['source_type'] = 'book'
        super().__init__(**data)


# Import here to avoid circular imports
from .note import NoteResponse
SourceDetail.model_rebuild()