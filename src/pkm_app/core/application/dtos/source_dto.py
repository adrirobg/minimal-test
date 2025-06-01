import uuid
from datetime import datetime
from typing import Any, Optional  # Removed Dict

from pydantic import AnyUrl, BaseModel, ConfigDict, Field

# --- Source Schemas ---


class SourceBase(BaseModel):
    """
    Base schema for source data.
    A source represents the origin of a note, like a book, article, or URL.
    """

    type: str | None = Field(
        default=None,
        max_length=100,
        description="Type of the source (e.g., 'article', 'book', 'website'). Corresponds to VARCHAR(100) in the database model.",
    )
    title: str | None = Field(default=None, description="Title of the source.")
    description: str | None = Field(default=None, description="A brief description of the source.")
    url: AnyUrl | None = Field(
        default=None, description="URL of the source, if applicable. Validated as a URL."
    )
    link_metadata: dict[str, Any] | None = Field(
        default_factory=lambda: {},
        description="Additional metadata related to the source, especially if it's a link.",
    )

    model_config = ConfigDict(
        extra="forbid",
    )


class SourceCreate(SourceBase):
    """
    Schema for creating a new source.
    Inherits fields from SourceBase.
    user_id will be assigned by the application logic.
    """

    pass


class SourceUpdate(BaseModel):
    """
    Schema for updating an existing source.
    All fields are optional.
    """

    type: str | None = Field(default=None, max_length=100, description="New type of the source.")
    title: str | None = Field(default=None, description="New title of the source.")
    description: str | None = Field(default=None, description="New description of the source.")
    url: AnyUrl | None = Field(default=None, description="New URL of the source.")
    link_metadata: dict[str, Any] | None = Field(
        default=None,
        description="New metadata for the source. If provided, replaces existing metadata.",
    )

    model_config = ConfigDict(
        extra="forbid",
    )


class SourceSchema(SourceBase):
    """
    Schema representing a source, including database-generated fields.
    This schema is typically used for responses.
    """

    id: uuid.UUID = Field(description="Unique identifier for the source.")
    user_id: str = Field(description="Identifier of the user who owns this source.")
    created_at: datetime = Field(description="Timestamp of when the source was created.")
    updated_at: datetime = Field(description="Timestamp of the last update to the source.")

    model_config = ConfigDict(
        from_attributes=True,  # Allow creating from ORM models
        frozen=True,  # Make instances immutable after creation
        extra="forbid",
    )
