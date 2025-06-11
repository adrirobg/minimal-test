import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

# --- NoteLink Schemas ---


class NoteLinkBase(BaseModel):
    """
    Base schema for note link data.
    A note link represents a connection between two notes.
    """

    link_type: str | None = Field(
        default="related",
        max_length=100,
        description="Type of link (e.g., 'related', 'cites', 'extends'). Corresponds to VARCHAR(100) in the database model.",
    )
    description: str | None = Field(
        default=None, description="A description of the link or its nature."
    )

    model_config = ConfigDict(
        extra="forbid",
    )


class NoteLinkCreate(NoteLinkBase):
    """
    Schema for creating a new note link.
    Requires source_note_id and target_note_id.
    user_id will be assigned by the application logic.
    """

    source_note_id: uuid.UUID = Field(description="ID of the source note in the link.")
    target_note_id: uuid.UUID = Field(description="ID of the target note in the link.")


class NoteLinkUpdate(BaseModel):
    """
    Schema for updating an existing note link.
    All fields are optional.
    """

    link_type: str | None = Field(default=None, max_length=100, description="New type of the link.")
    description: str | None = Field(default=None, description="New description of the link.")

    model_config = ConfigDict(
        extra="forbid",
    )


class NoteLinkSchema(NoteLinkBase):
    """
    Schema representing a note link, including database-generated fields.
    This schema is typically used for responses.
    """

    id: uuid.UUID = Field(description="Unique identifier for the note link.")
    source_note_id: uuid.UUID = Field(description="ID of the source note in the link.")
    target_note_id: uuid.UUID = Field(description="ID of the target note in the link.")
    user_id: str = Field(
        description="Identifier of the user who owns this note link."
    )  # Included as it's in the SQLAlchemy model
    created_at: datetime = Field(description="Timestamp of when the note link was created.")

    model_config = ConfigDict(
        from_attributes=True,  # Allow creating from ORM models
        frozen=True,  # Make instances immutable after creation
        extra="forbid",
    )
