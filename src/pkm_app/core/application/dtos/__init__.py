"""
Data Transfer Objects (DTOs) for the application layer.

This package modularizes DTOs by entity. It is recommended to import DTOs
directly from their specific modules for clarity, for example:
`from pkm_app.core.application.dtos.note_dto import NoteSchema`

However, for convenience or maintaining backward compatibility during transition,
key DTOs are also re-exported here.
"""

from .keyword_dto import (
    KeywordBase,
    KeywordCreate,
    KeywordSchema,
    KeywordUpdate,
)
from .note_dto import (
    NoteBase,
    NoteCreate,
    NoteSchema,
    NoteUpdate,
    NoteWithLinksSchema,
)
from .note_link_dto import (
    NoteLinkBase,
    NoteLinkCreate,
    NoteLinkSchema,
    NoteLinkUpdate,
)
from .project_dto import (
    ProjectBase,
    ProjectCreate,
    ProjectSchema,
    ProjectUpdate,
)
from .source_dto import (
    SourceBase,
    SourceCreate,
    SourceSchema,
    SourceUpdate,
)
from .user_profile_dto import (
    UserProfileBase,
    UserProfileCreate,
    UserProfileSchema,
    UserProfileUpdate,
)

__all__ = [
    # UserProfile DTOs
    "UserProfileBase",
    "UserProfileCreate",
    "UserProfileUpdate",
    "UserProfileSchema",
    # Keyword DTOs
    "KeywordBase",
    "KeywordCreate",
    "KeywordUpdate",
    "KeywordSchema",
    # Project DTOs
    "ProjectBase",
    "ProjectCreate",
    "ProjectUpdate",
    "ProjectSchema",
    # Source DTOs
    "SourceBase",
    "SourceCreate",
    "SourceUpdate",
    "SourceSchema",
    # NoteLink DTOs
    "NoteLinkBase",
    "NoteLinkCreate",
    "NoteLinkUpdate",
    "NoteLinkSchema",
    # Note DTOs
    "NoteBase",
    "NoteCreate",
    "NoteUpdate",
    "NoteSchema",
    "NoteWithLinksSchema",
]
