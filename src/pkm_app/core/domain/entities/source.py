"""Source entity module"""

import re
from typing import Optional
from urllib.parse import urlparse

from pydantic import AnyHttpUrl, Field, HttpUrl, ValidationError, field_validator

from .entity import Entity

VALID_SOURCE_TYPES = ["article", "book", "website", "video"]


class Source(Entity):
    """Domain entity representing an external source of information"""

    title: str = Field(description="Title of the source", max_length=200, min_length=1)

    source_type: str = Field(description="Type of the source (article, book, etc.)")

    url: str | None = Field(default=None, description="URL of the source if available")

    metadata: dict = Field(
        default_factory=dict, description="Additional metadata specific to the source type"
    )

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        """Validate source title"""
        if not value or value.isspace():
            raise ValueError("Source title cannot be empty or whitespace")
        return value

    @field_validator("source_type")
    @classmethod
    def validate_source_type(cls, value: str) -> str:
        """Validate that the source type is one of the allowed values"""
        if value not in VALID_SOURCE_TYPES:
            raise ValueError(
                f"Invalid source type. Must be one of: {', '.join(VALID_SOURCE_TYPES)}"
            )
        return value

    @field_validator("url")
    @classmethod
    def validate_url(cls, value: str | None) -> str | None:
        """Validate source URL if provided"""
        if value is None:
            return None

        if not value:
            raise ValueError("URL cannot be empty string, use None instead")

        try:
            # Parse URL to validate format
            parsed = urlparse(value)

            # Check scheme
            if parsed.scheme not in ["http", "https"]:
                raise ValueError("URL must use http or https scheme")

            # Check if has domain
            if not parsed.netloc:
                raise ValueError("Invalid URL format")

            # Try to parse as HttpUrl to ensure full validation
            HttpUrl(value)

            return value

        except Exception as e:
            raise ValueError(f"Invalid URL format: {str(e)}") from e

    @field_validator("metadata")
    @classmethod
    def validate_metadata(cls, value: dict) -> dict:
        """Validate source metadata structure"""
        if not isinstance(value, dict):
            raise ValueError("Metadata must be a dictionary")
        return value
