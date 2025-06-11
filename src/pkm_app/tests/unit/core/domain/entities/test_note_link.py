"""Tests for the NoteLink entity"""

import uuid
from datetime import datetime, timezone
import pytest
from pydantic import ValidationError
from pkm_app.core.domain.entities.note_link import NoteLink


def test_notelink_creation_valid():
    """Test creating a valid note link"""
    # Arrange
    now = datetime.now(timezone.utc)
    link_data = {
        "id": uuid.uuid4(),
        "created_at": now,
        "updated_at": now,
        "source_note_id": uuid.uuid4(),
        "target_note_id": uuid.uuid4(),
        "link_type": "reference",
        "metadata": {"strength": 1},
    }

    # Act
    link = NoteLink(**link_data)

    # Assert
    assert link.id == link_data["id"]
    assert link.source_note_id == link_data["source_note_id"]
    assert link.target_note_id == link_data["target_note_id"]
    assert link.link_type == link_data["link_type"]
    assert link.metadata == link_data["metadata"]


def test_notelink_different_notes():
    """Test validation that source and target notes must be different"""
    # Arrange
    now = datetime.now(timezone.utc)
    same_note_id = uuid.uuid4()
    link_data = {
        "id": uuid.uuid4(),
        "created_at": now,
        "updated_at": now,
        "source_note_id": same_note_id,
        "target_note_id": same_note_id,
        "link_type": "reference",
    }

    # Act & Assert
    with pytest.raises(ValidationError, match="Source and target notes must be different"):
        NoteLink(**link_data)


def test_notelink_valid_types():
    """Test validation of link types"""
    # Arrange
    now = datetime.now(timezone.utc)
    base_data = {
        "id": uuid.uuid4(),
        "created_at": now,
        "updated_at": now,
        "source_note_id": uuid.uuid4(),
        "target_note_id": uuid.uuid4(),
    }

    # Act & Assert - Valid types
    valid_types = ["reference", "relates_to", "depends_on", "contradicts", "supports"]
    for link_type in valid_types:
        link = NoteLink(**{**base_data, "link_type": link_type})
        assert link.link_type == link_type

    # Act & Assert - Invalid type
    with pytest.raises(ValidationError, match="Invalid link type"):
        NoteLink(**{**base_data, "link_type": "invalid_type"})


def test_notelink_metadata_validation():
    """Test validation of link metadata"""
    # Arrange
    now = datetime.now(timezone.utc)
    base_data = {
        "id": uuid.uuid4(),
        "created_at": now,
        "updated_at": now,
        "source_note_id": uuid.uuid4(),
        "target_note_id": uuid.uuid4(),
        "link_type": "reference",
    }

    # Act & Assert - Valid metadata
    valid_metadata = {"strength": 1, "description": "test link"}
    link = NoteLink(**{**base_data, "metadata": valid_metadata})
    assert link.metadata == valid_metadata

    # Act & Assert - Default metadata when not provided
    link = NoteLink(**base_data)
    assert link.metadata == {}

    # Act & Assert - Invalid metadata (not a dict)
    with pytest.raises(ValidationError, match="Input should be a valid dictionary"):
        NoteLink(**{**base_data, "metadata": ["invalid"]})
