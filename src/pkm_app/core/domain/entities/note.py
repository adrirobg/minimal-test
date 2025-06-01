"""Note entity module"""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import Field, field_validator

from .entity import Entity

VALID_NOTE_TYPES = ["markdown", "text", "code", "mixed"]


class Note(Entity):
    """Core domain entity representing a note in the PKM system"""

    title: str = Field(description="Title of the note", max_length=200, min_length=1)

    content: str = Field(description="Main content of the note")

    type: str = Field(description="Type of note content", max_length=100)

    metadata: dict = Field(default_factory=dict, description="Additional metadata for the note")

    project_id: uuid.UUID | None = Field(
        default=None, description="ID of the project this note belongs to"
    )

    source_id: uuid.UUID | None = Field(
        default=None, description="ID of the source this note is derived from"
    )

    keyword_ids: list[uuid.UUID] = Field(
        default_factory=list, description="IDs of keywords associated with this note"
    )

    @field_validator("type")
    @classmethod
    def validate_note_type(cls, value: str) -> str:
        """Validate that the note type is one of the allowed values"""
        if value not in VALID_NOTE_TYPES:
            raise ValueError(f"Invalid note type. Must be one of: {', '.join(VALID_NOTE_TYPES)}")
        return value

    @field_validator("metadata")
    @classmethod
    def validate_metadata(cls, value: dict) -> dict:
        """Validate note metadata structure"""
        if not isinstance(value, dict):
            raise ValueError("Metadata must be a dictionary")
        return value

    @field_validator("keyword_ids")
    @classmethod
    def validate_keyword_ids(cls, value: list[uuid.UUID]) -> list[uuid.UUID]:
        """Validate list of keyword IDs"""
        if not isinstance(value, list):
            raise ValueError("keyword_ids must be a list")
        return value
