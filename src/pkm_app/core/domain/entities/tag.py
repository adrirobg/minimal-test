"""Tag entity module"""

import re
import uuid
from typing import Optional

from pydantic import Field, ValidationInfo, field_validator

from .entity import Entity


class Tag(Entity):
    """Domain entity representing a system tag for categorization"""

    name: str = Field(
        description="System tag name in dot notation (e.g., system.category.subcategory)",
        max_length=100,
    )

    metadata: dict = Field(default_factory=dict, description="Additional metadata for the tag")

    parent_id: uuid.UUID | None = Field(
        default=None, description="ID of the parent tag in the hierarchy"
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        """Validate tag name format"""
        if not value or value.isspace():
            raise ValueError("Tag name cannot be empty or whitespace")

        # Must start with 'system.'
        if not value.startswith("system."):
            raise ValueError("Tag name must start with 'system.'")

        # Check format (dot notation with valid characters)
        if not re.match(r"^system\.[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*$", value):
            raise ValueError(
                "Invalid tag name format. Must be dot notation with alphanumeric characters and hyphens"
            )

        return value

    @field_validator("parent_id")
    @classmethod
    def validate_parent_id(cls, value: uuid.UUID | None, info: ValidationInfo) -> uuid.UUID | None:
        """Validate parent tag reference"""
        if value is not None and info.data and "id" in info.data and value == info.data["id"]:
            raise ValueError("Tag cannot reference itself as parent")
        return value

    @field_validator("metadata")
    @classmethod
    def validate_metadata(cls, value: dict) -> dict:
        """Validate tag metadata structure"""
        if not isinstance(value, dict):
            raise ValueError("Metadata must be a dictionary")
        return value
