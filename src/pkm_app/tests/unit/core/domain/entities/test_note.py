"""Tests for the Note entity"""

import uuid
from datetime import datetime, timezone
import pytest
from pydantic import ValidationError
from pkm_app.core.domain.entities.note import Note


def test_note_creation_valid():
    """Test creating a valid note with all required fields"""
    # Arrange
    now = datetime.now(timezone.utc)
    note_data = {
        "id": uuid.uuid4(),
        "created_at": now,
        "updated_at": now,
        "title": "Test Note",
        "content": "This is a test note content",
        "type": "markdown",
        "metadata": {"tags": ["test"], "priority": 1},
        "project_id": uuid.uuid4(),
        "source_id": uuid.uuid4(),
        "keyword_ids": [uuid.uuid4(), uuid.uuid4()],
    }

    # Act
    note = Note(**note_data)

    # Assert
    assert note.id == note_data["id"]
    assert note.title == note_data["title"]
    assert note.content == note_data["content"]
    assert note.type == note_data["type"]
    assert note.metadata == note_data["metadata"]
    assert note.project_id == note_data["project_id"]
    assert note.source_id == note_data["source_id"]
    assert note.keyword_ids == note_data["keyword_ids"]


def test_note_content_required():
    """Test that note content is required"""
    # Arrange
    now = datetime.now(timezone.utc)
    note_data = {
        "id": uuid.uuid4(),
        "created_at": now,
        "updated_at": now,
        "title": "Test Note",
        "type": "markdown",
    }

    # Act & Assert
    with pytest.raises(ValidationError, match="Field required"):
        Note(**note_data)


def test_note_type_validation():
    """Test note type validation"""
    # Arrange
    now = datetime.now(timezone.utc)
    valid_types = ["markdown", "text", "code", "mixed"]
    invalid_type = "invalid_type"
    base_data = {
        "id": uuid.uuid4(),
        "created_at": now,
        "updated_at": now,
        "title": "Test Note",
        "content": "Test content",
    }

    # Act & Assert - Valid types
    for note_type in valid_types:
        note = Note(**{**base_data, "type": note_type})
        assert note.type == note_type

    # Act & Assert - Invalid type
    with pytest.raises(ValidationError, match="Invalid note type"):
        Note(**{**base_data, "type": invalid_type})

    # Act & Assert - Type length validation
    with pytest.raises(ValidationError, match="String should have at most 100 characters"):
        Note(**{**base_data, "type": "x" * 101})


def test_note_metadata_validation():
    """Test note metadata validation"""
    # Arrange
    now = datetime.now(timezone.utc)
    base_data = {
        "id": uuid.uuid4(),
        "created_at": now,
        "updated_at": now,
        "title": "Test Note",
        "content": "Test content",
        "type": "markdown",
    }

    # Act & Assert - Valid metadata
    valid_metadata = {"tags": ["test"], "priority": 1}
    note = Note(**{**base_data, "metadata": valid_metadata})
    assert note.metadata == valid_metadata

    # Act & Assert - Default metadata when not provided
    note = Note(**base_data)
    assert note.metadata == {}


def test_note_relationships():
    """Test note relationships validation"""
    # Arrange
    now = datetime.now(timezone.utc)
    base_data = {
        "id": uuid.uuid4(),
        "created_at": now,
        "updated_at": now,
        "title": "Test Note",
        "content": "Test content",
        "type": "markdown",
    }

    # Act & Assert - Valid relationships
    project_id = uuid.uuid4()
    source_id = uuid.uuid4()
    keyword_ids = [uuid.uuid4(), uuid.uuid4()]

    note = Note(
        **{
            **base_data,
            "project_id": project_id,
            "source_id": source_id,
            "keyword_ids": keyword_ids,
        }
    )

    assert note.project_id == project_id
    assert note.source_id == source_id
    assert note.keyword_ids == keyword_ids

    # Act & Assert - Optional relationships
    note = Note(**base_data)
    assert note.project_id is None
    assert note.source_id is None
    assert note.keyword_ids == []
