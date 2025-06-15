"""
Project Pydantic schemas for validation and serialization
"""
import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, field_validator


class ProjectBase(BaseModel):
    """Base Project schema with common fields."""
    name: str
    description: Optional[str] = None
    parent_project_id: Optional[uuid.UUID] = None
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Project name cannot be empty')
        if len(v.strip()) < 2:
            raise ValueError('Project name must be at least 2 characters long')
        if len(v.strip()) > 200:
            raise ValueError('Project name cannot exceed 200 characters')
        return v.strip()


class ProjectCreate(ProjectBase):
    """Schema for creating a new project."""
    pass


class ProjectUpdate(BaseModel):
    """Schema for updating project information."""
    name: Optional[str] = None
    description: Optional[str] = None
    parent_project_id: Optional[uuid.UUID] = None
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not v or not v.strip():
            raise ValueError('Project name cannot be empty')
        if len(v.strip()) < 2:
            raise ValueError('Project name must be at least 2 characters long')
        if len(v.strip()) > 200:
            raise ValueError('Project name cannot exceed 200 characters')
        return v.strip()


class ProjectInDB(ProjectBase):
    """Schema for project data as stored in database."""
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ProjectResponse(ProjectBase):
    """Schema for project data in API responses."""
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ProjectWithNotes(ProjectResponse):
    """Schema for project with associated notes."""
    notes_count: int = 0
    
    class Config:
        from_attributes = True


class ProjectTree(ProjectResponse):
    """Schema for hierarchical project structure."""
    children: List['ProjectTree'] = []
    notes_count: int = 0
    total_notes_count: int = 0  # Including children
    
    class Config:
        from_attributes = True


# Update forward reference for recursive model
ProjectTree.model_rebuild()