"""Keyword entity module"""

import re
import uuid

from pydantic import Field, computed_field, field_validator

from .entity import Entity


class Keyword(Entity):
    """Domain entity representing a keyword/tag for categorization"""

    name: str = Field(description="Original keyword name", max_length=100, min_length=1)

    user_id: uuid.UUID = Field(description="ID of the user who owns this keyword")

    @computed_field  # No @property needed here with Pydantic v2
    def normalized_name(self) -> str:
        """Get the normalized version of the keyword name"""
        # Convert to lowercase
        normalized = self.name.lower()

        # Replace multiple spaces with single space and trim
        normalized = " ".join(normalized.split())

        # Replace spaces and underscores with hyphens
        normalized = re.sub(r"[\s_]+", "-", normalized)

        # Remove any other special characters
        normalized = re.sub(r"[^a-z0-9\-\.]", "", normalized)

        return normalized

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        """Validate keyword name format"""
        # Check for empty or whitespace-only strings
        if not value or value.isspace():
            raise ValueError("Keyword name cannot be empty or whitespace")

        # Check for invalid characters
        if re.search(r"[@/\\]", value):
            raise ValueError("Keyword name contains invalid characters")

        return value
