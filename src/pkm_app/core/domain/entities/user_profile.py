"""UserProfile entity module"""

import re
from datetime import UTC, datetime, timezone
from typing import Optional

from pydantic import EmailStr, Field, field_validator

from .entity import Entity


class UserProfile(Entity):
    """Domain entity representing a user's profile and preferences"""

    username: str = Field(description="Unique username for the user", min_length=3, max_length=50)

    email: EmailStr = Field(description="User's email address")

    display_name: str | None = Field(
        default=None, description="User's display name", max_length=100
    )

    preferences: dict = Field(default_factory=dict, description="User's preferences and settings")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        """Validate username format"""
        if not value or value.isspace():
            raise ValueError("Username cannot be empty or whitespace")

        # Check for invalid characters
        if not re.match(r"^[a-zA-Z0-9_-]+$", value):
            raise ValueError("Username can only contain letters, numbers, underscores, and hyphens")

        return value

    @field_validator("display_name")
    @classmethod
    def validate_display_name(cls, value: str | None) -> str | None:
        """Validate display name if provided"""
        if value is not None and (not value or value.isspace()):
            raise ValueError("Display name cannot be empty or whitespace")
        return value

    @field_validator("preferences")
    @classmethod
    def validate_preferences(cls, value: dict) -> dict:
        """Validate user preferences structure"""
        if not isinstance(value, dict):
            raise ValueError("Preferences must be a dictionary")
        return value
