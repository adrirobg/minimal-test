"""Project entity module"""

import re
from typing import Optional

from pydantic import Field, field_validator

from .entity import Entity

VALID_PROJECT_STATUSES = ["active", "completed", "archived", "on_hold"]


class Project(Entity):
    """Domain entity representing a project that groups related notes"""

    name: str = Field(description="Name of the project", max_length=100, min_length=1)

    description: str = Field(
        default="", description="Detailed description of the project", max_length=500
    )

    status: str = Field(default="active", description="Current status of the project")

    metadata: dict = Field(default_factory=dict, description="Additional metadata for the project")

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        """Validate project name format"""
        if not value or value.isspace():
            raise ValueError("Project name cannot be empty or whitespace")

        # Check for invalid characters
        if re.search(r"[/\\]", value):
            raise ValueError("Project name contains invalid characters")

        return value

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str) -> str:
        """Validate that the project status is one of the allowed values"""
        if value not in VALID_PROJECT_STATUSES:
            raise ValueError(
                f"Invalid project status. Must be one of: {', '.join(VALID_PROJECT_STATUSES)}"
            )
        return value

    @field_validator("metadata")
    @classmethod
    def validate_metadata(cls, value: dict) -> dict:
        """Validate project metadata structure"""
        if not isinstance(value, dict):
            raise ValueError("Metadata must be a dictionary")
        return value
