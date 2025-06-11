import uuid
from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

# --- UserProfile Schemas ---


class UserProfileDTO(BaseModel):
    """
    Data Transfer Object for UserProfile.
    Used in application layer use cases.
    """

    id: UUID
    username: str
    email: EmailStr

    @classmethod
    def from_entity(cls, entity: Any) -> "UserProfileDTO":
        """
        Create a UserProfileDTO from a UserProfile entity.
        """
        return cls(id=entity.id, username=entity.username, email=entity.email)


class UserProfileBase(BaseModel):
    """
    Base schema for user profile data.
    """

    name: str | None = Field(default=None, description="User's full name.")
    email: EmailStr | None = Field(default=None, description="User's email address.")
    preferences: dict[str, Any] | None = Field(None, description="User preferences")
    learned_context: dict[str, Any] | None = Field(
        default_factory=lambda: {}, description="Context learned by the system about the user."
    )

    model_config = ConfigDict(
        extra="forbid",  # Disallow extra fields
    )


class UserProfileCreate(UserProfileBase):
    """
    Schema for creating a new user profile.
    Requires user_id.
    """

    user_id: str = Field(
        description="Unique identifier for the user (e.g., from an auth provider)."
    )


class UserProfileUpdate(UserProfileBase):
    """
    Schema for updating an existing user profile.
    All fields are optional.
    """

    name: str | None = Field(default=None, description="User's full name.")
    email: EmailStr | None = Field(default=None, description="User's email address.")
    preferences: dict[str, Any] | None = Field(None, description="User preferences")
    learned_context: dict[str, Any] | None = Field(
        default=None,
        description="Context learned by the system. If provided, replaces existing learned context.",
    )

    model_config = ConfigDict(
        extra="forbid",
    )


class UserProfileSchema(UserProfileBase):
    """
    Schema representing a user profile, including database-generated fields.
    This schema is typically used for responses.
    """

    user_id: str = Field(description="Unique identifier for the user.")
    created_at: datetime = Field(description="Timestamp of when the profile was created.")
    updated_at: datetime = Field(description="Timestamp of the last update to the profile.")

    model_config = ConfigDict(
        from_attributes=True,  # Allow creating from ORM models
        frozen=True,  # Make instances immutable after creation
        extra="forbid",
    )
