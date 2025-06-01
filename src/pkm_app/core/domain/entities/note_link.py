"""NoteLink entity module"""

import uuid

from pydantic import Field, ValidationInfo, field_validator

from .entity import Entity

VALID_LINK_TYPES = ["reference", "relates_to", "depends_on", "contradicts", "supports"]


class NoteLink(Entity):
    """Domain entity representing a directed relationship between notes"""

    source_note_id: uuid.UUID = Field(description="ID of the source note in the relationship")

    target_note_id: uuid.UUID = Field(description="ID of the target note in the relationship")

    link_type: str = Field(description="Type of relationship between the notes")

    metadata: dict = Field(
        default_factory=dict, description="Additional metadata about the relationship"
    )

    @field_validator("target_note_id")
    @classmethod
    def validate_different_notes(cls, value: uuid.UUID, info: ValidationInfo) -> uuid.UUID:
        """Validate that source and target notes are different"""
        if info.data and "source_note_id" in info.data and value == info.data["source_note_id"]:
            raise ValueError("Source and target notes must be different")
        return value

    @field_validator("link_type")
    @classmethod
    def validate_link_type(cls, value: str) -> str:
        """Validate that the link type is one of the allowed values"""
        if value not in VALID_LINK_TYPES:
            raise ValueError(f"Invalid link type. Must be one of: {', '.join(VALID_LINK_TYPES)}")
        return value

    @field_validator("metadata")
    @classmethod
    def validate_metadata(cls, value: dict) -> dict:
        """Validate relationship metadata structure"""
        if not isinstance(value, dict):
            raise ValueError("Metadata must be a dictionary")
        return value
