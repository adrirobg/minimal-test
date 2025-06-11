import uuid
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field

from .keyword_dto import KeywordSchema
from .note_link_dto import NoteLinkSchema
from .project_dto import ProjectSchema
from .source_dto import SourceSchema

# --- Note Schemas ---


class NoteBase(BaseModel):
    """
    Base schema for note data.
    """

    title: str | None = Field(default=None, description="Title of the note.")
    content: str = Field(description="Main content of the note.")
    type: str | None = Field(
        default=None,
        max_length=100,
        description="Type of the note (e.g., 'fleeting', 'permanent'). Corresponds to VARCHAR(100) in the database model.",
    )
    note_metadata: dict[str, Any] | None = Field(
        default_factory=lambda: {}, description="Additional metadata for the note."
    )
    project_id: uuid.UUID | None = Field(
        default=None, description="ID of the project this note belongs to, if any."
    )
    source_id: uuid.UUID | None = Field(
        default=None, description="ID of the source this note is derived from, if any."
    )

    model_config = ConfigDict(
        extra="forbid",
    )


class NoteCreate(NoteBase):
    """
    Schema for creating a new note.
    Inherits fields from NoteBase.
    user_id and keyword associations are handled by application logic.
    """

    keywords: list[str] | None = Field(
        default=None, description="List of keyword names to associate with the note."
    )


class NoteUpdate(BaseModel):
    """
    Schema for updating an existing note.
    All fields are optional.
    """

    title: str | None = Field(default=None, description="New title for the note.")
    content: str | None = Field(default=None, description="New content for the note.")
    type: str | None = Field(default=None, max_length=100, description="New type for the note.")
    note_metadata: dict[str, Any] | None = Field(
        default=None,
        description="New metadata for the note. If provided, replaces existing metadata.",
    )
    project_id: uuid.UUID | None = Field(default=None, description="New project ID for the note.")
    source_id: uuid.UUID | None = Field(default=None, description="New source ID for the note.")
    keywords: list[str] | None = Field(
        default=None,
        description="List of keyword names to associate/update for the note. Provide an empty list to remove all keywords.",
    )
    # Updating links is typically handled via specific endpoints/logic.

    model_config = ConfigDict(
        extra="forbid",
    )


class NoteSchema(NoteBase):
    """
    Schema representing a note, including database-generated fields and basic relationships.
    This schema is typically used for responses.
    """

    id: uuid.UUID = Field(description="Unique identifier for the note.")
    user_id: str = Field(description="Identifier of the user who owns this note.")
    created_at: datetime = Field(description="Timestamp of when the note was created.")
    updated_at: datetime = Field(description="Timestamp of the last update to the note.")

    project: ProjectSchema | None = Field(
        default=None, description="The project associated with this note, if any."
    )
    source: SourceSchema | None = Field(
        default=None, description="The source associated with this note, if any."
    )
    keywords: list[KeywordSchema] = Field(
        default_factory=list, description="List of keywords associated with this note."
    )

    model_config = ConfigDict(
        from_attributes=True,  # Allow creating from ORM models
        frozen=True,  # Make instances immutable after creation
        extra="forbid",
    )


class NoteWithLinksSchema(NoteSchema):
    """
    Extended schema for a note that includes its direct links (source of and target of).
    Useful for specific use cases requiring link details alongside the note.
    """

    source_of_links: list[NoteLinkSchema] = Field(
        default_factory=list, description="List of links where this note is the source."
    )
    target_of_links: list[NoteLinkSchema] = Field(
        default_factory=list, description="List of links where this note is the target."
    )

    model_config = ConfigDict(
        from_attributes=True,
        frozen=True,
        extra="forbid",
    )
