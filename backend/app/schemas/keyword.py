"""
Keyword Pydantic schemas for validation and serialization
"""
import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, field_validator


class KeywordBase(BaseModel):
    """Base Keyword schema with common fields."""
    name: str
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Keyword name cannot be empty')
        if len(v.strip()) < 1:
            raise ValueError('Keyword name must be at least 1 character long')
        if len(v.strip()) > 100:
            raise ValueError('Keyword name cannot exceed 100 characters')
        # Normalize keyword (lowercase, no extra spaces)
        return v.strip().lower()


class KeywordCreate(KeywordBase):
    """Schema for creating a new keyword."""
    pass


class KeywordUpdate(BaseModel):
    """Schema for updating keyword information."""
    name: Optional[str] = None
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not v or not v.strip():
            raise ValueError('Keyword name cannot be empty')
        if len(v.strip()) < 1:
            raise ValueError('Keyword name must be at least 1 character long')
        if len(v.strip()) > 100:
            raise ValueError('Keyword name cannot exceed 100 characters')
        return v.strip().lower()


class KeywordInDB(KeywordBase):
    """Schema for keyword data as stored in database."""
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class KeywordResponse(KeywordBase):
    """Schema for keyword data in API responses."""
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class KeywordWithNotes(KeywordResponse):
    """Schema for keyword with associated notes count."""
    notes_count: int = 0
    
    class Config:
        from_attributes = True


class KeywordStats(KeywordResponse):
    """Schema for keyword statistics."""
    notes_count: int = 0
    recent_notes: List['NoteResponse'] = []
    
    class Config:
        from_attributes = True


class KeywordSearch(BaseModel):
    """Schema for keyword search parameters."""
    query: Optional[str] = None
    limit: int = 20
    offset: int = 0
    include_stats: bool = False
    
    @field_validator('limit')
    @classmethod
    def validate_limit(cls, v: int) -> int:
        if v < 1 or v > 100:
            raise ValueError('Limit must be between 1 and 100')
        return v


# Import here to avoid circular imports
from .note import NoteResponse
KeywordStats.model_rebuild()