"""
Pydantic schemas package for Kairos BCP PKM system
"""
# User schemas
from .user import (
    UserCreate, UserUpdate, UserResponse, UserInDB, 
    UserLogin, UserProfile
)

# Project schemas  
from .project import (
    ProjectCreate, ProjectUpdate, ProjectResponse, ProjectInDB,
    ProjectWithNotes, ProjectTree
)

# Note schemas
from .note import (
    NoteCreate, NoteUpdate, NoteResponse, NoteInDB,
    NoteWithKeywords, NoteWithProject, NoteWithSource, 
    NoteDetail, NoteSearch
)

# Keyword schemas
from .keyword import (
    KeywordCreate, KeywordUpdate, KeywordResponse, KeywordInDB,
    KeywordWithNotes, KeywordStats, KeywordSearch
)

# Source schemas
from .source import (
    SourceCreate, SourceUpdate, SourceResponse, SourceInDB,
    SourceWithNotes, SourceDetail, SourceSearch,
    WebSourceCreate, BookSourceCreate
)

# Auth schemas
from .auth import (
    Token, TokenData, RefreshToken, PasswordReset, PasswordResetConfirm
)

# Common schemas
from .common import (
    PaginatedResponse, MessageResponse, ErrorResponse, HealthResponse,
    SearchResponse, BulkOperationResponse, StatsResponse
)

__all__ = [
    # User schemas
    "UserCreate", "UserUpdate", "UserResponse", "UserInDB", 
    "UserLogin", "UserProfile",
    
    # Project schemas
    "ProjectCreate", "ProjectUpdate", "ProjectResponse", "ProjectInDB",
    "ProjectWithNotes", "ProjectTree",
    
    # Note schemas
    "NoteCreate", "NoteUpdate", "NoteResponse", "NoteInDB",
    "NoteWithKeywords", "NoteWithProject", "NoteWithSource", 
    "NoteDetail", "NoteSearch",
    
    # Keyword schemas
    "KeywordCreate", "KeywordUpdate", "KeywordResponse", "KeywordInDB",
    "KeywordWithNotes", "KeywordStats", "KeywordSearch",
    
    # Source schemas
    "SourceCreate", "SourceUpdate", "SourceResponse", "SourceInDB",
    "SourceWithNotes", "SourceDetail", "SourceSearch",
    "WebSourceCreate", "BookSourceCreate",
    
    # Auth schemas
    "Token", "TokenData", "RefreshToken", "PasswordReset", "PasswordResetConfirm",
    
    # Common schemas
    "PaginatedResponse", "MessageResponse", "ErrorResponse", "HealthResponse",
    "SearchResponse", "BulkOperationResponse", "StatsResponse",
]