"""Tests for the Source entity"""

import uuid
from datetime import datetime, timezone
import pytest
from pydantic import ValidationError
from pkm_app.core.domain.entities.source import Source


def test_source_creation_valid():
    """Test creating a valid source"""
    # Arrange
    now = datetime.now(timezone.utc)
    source_data = {
        "id": uuid.uuid4(),
        "created_at": now,
        "updated_at": now,
        "title": "Test Source",
        "source_type": "article",
        "url": "https://example.com/article",
        "metadata": {"author": "Test Author", "publication_date": "2025-01-01"},
    }

    # Act
    source = Source(**source_data)

    # Assert
    assert source.id == source_data["id"]
    assert source.title == source_data["title"]
    assert source.source_type == source_data["source_type"]
    assert source.url == source_data["url"]
    assert source.metadata == source_data["metadata"]


def test_source_url_validation():
    """Test source URL validation"""
    # Arrange
    now = datetime.now(timezone.utc)
    base_data = {
        "id": uuid.uuid4(),
        "created_at": now,
        "updated_at": now,
        "title": "Test Source",
        "source_type": "article",
    }

    # Act & Assert - Valid URLs
    valid_urls = [
        "https://example.com",
        "http://test.org/path",
        "https://sub.domain.com/path?param=value",
        None,  # URL is optional
    ]

    for url in valid_urls:
        source = Source(**{**base_data, "url": url})
        assert source.url == url

    # Act & Assert - Empty string URL
    with pytest.raises(ValidationError, match="URL cannot be empty string"):
        Source(**{**base_data, "url": ""})

    # Act & Assert - Invalid URLs
    invalid_urls = ["not-a-url", "ftp://invalid-scheme.com", "http:/missing-slash.com"]

    for url in invalid_urls:
        with pytest.raises(ValidationError):
            Source(**{**base_data, "url": url})


def test_source_type_metadata():
    """Test source type and metadata validation"""
    # Arrange
    now = datetime.now(timezone.utc)
    base_data = {"id": uuid.uuid4(), "created_at": now, "updated_at": now, "title": "Test Source"}

    # Act & Assert - Valid types and metadata
    valid_types = [
        ("article", {"author": "Test Author", "journal": "Test Journal"}),
        ("book", {"author": "Test Author", "isbn": "1234567890"}),
        ("website", {"domain": "example.com"}),
        ("video", {"duration": "10:00", "platform": "YouTube"}),
    ]

    for source_type, metadata in valid_types:
        source = Source(**{**base_data, "source_type": source_type, "metadata": metadata})
        assert source.source_type == source_type
        assert source.metadata == metadata

    # Act & Assert - Invalid type
    with pytest.raises(ValidationError, match="Invalid source type"):
        Source(**{**base_data, "source_type": "invalid_type"})

    # Act & Assert - Invalid metadata (not a dict)
    with pytest.raises(ValidationError, match="Input should be a valid dictionary"):
        Source(**{**base_data, "source_type": "article", "metadata": ["invalid"]})


def test_source_title_validation():
    """Test source title validation"""
    # Arrange
    now = datetime.now(timezone.utc)
    base_data = {"id": uuid.uuid4(), "created_at": now, "updated_at": now, "source_type": "article"}

    # Act & Assert - Empty title
    with pytest.raises(ValidationError, match="String should have at least 1 character"):
        Source(**{**base_data, "title": ""})

    # Act & Assert - Too long title
    with pytest.raises(ValidationError, match="String should have at most 200 characters"):
        Source(**{**base_data, "title": "x" * 201})

    # Act & Assert - Valid title
    source = Source(**{**base_data, "title": "Valid Title"})
    assert source.title == "Valid Title"
