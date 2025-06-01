"""Base entity module for domain entities"""

import uuid
from abc import ABC
from datetime import datetime
from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Entity(BaseModel, ABC):
    """Base class for all domain entities with common fields and validation"""

    model_config: ClassVar[ConfigDict] = ConfigDict(
        frozen=True,  # Make instances immutable
        validate_default=True,
        extra="forbid",  # Prevent extra attributes
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Unique identifier of the entity")

    created_at: datetime = Field(description="Timestamp when the entity was created")

    updated_at: datetime = Field(description="Timestamp when the entity was last updated")

    @field_validator("created_at", "updated_at")
    @classmethod
    def validate_timezone(cls, value: datetime) -> datetime:
        """Validate that timestamps are timezone-aware"""
        if value.tzinfo is None:
            raise ValueError("Timestamp must be a timezone-aware datetime")
        return value
