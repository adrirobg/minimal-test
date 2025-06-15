"""
Common Pydantic schemas and response models
"""
from typing import Generic, TypeVar, List, Optional, Any
from pydantic import BaseModel


T = TypeVar('T')


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response schema."""
    items: List[T]
    total: int
    limit: int
    offset: int
    has_next: bool
    has_previous: bool


class MessageResponse(BaseModel):
    """Simple message response schema."""
    message: str


class ErrorResponse(BaseModel):
    """Error response schema."""
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response schema."""
    status: str
    service: str
    version: str
    environment: str


class SearchResponse(BaseModel, Generic[T]):
    """Generic search response schema."""
    results: List[T]
    total: int
    query: Optional[str] = None
    limit: int
    offset: int


class BulkOperationResponse(BaseModel):
    """Bulk operation response schema."""
    success_count: int
    error_count: int
    errors: List[str] = []


class StatsResponse(BaseModel):
    """Statistics response schema."""
    total_users: int
    total_projects: int
    total_notes: int
    total_keywords: int
    total_sources: int