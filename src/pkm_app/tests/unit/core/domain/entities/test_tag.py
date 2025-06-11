"""Tests for the Tag entity"""

import uuid
from datetime import datetime, timezone
import pytest
from pydantic import ValidationError
from pkm_app.core.domain.entities.tag import Tag


def test_tag_creation_valid():
    """Test creating a valid tag"""
    # Arrange
    now = datetime.now(timezone.utc)
    tag_data = {
        "id": uuid.uuid4(),
        "created_at": now,
        "updated_at": now,
        "name": "system.category.test",
        "metadata": {"description": "Test tag"},
        "parent_id": None,
    }

    # Act
    tag = Tag(**tag_data)

    # Assert
    assert tag.id == tag_data["id"]
    assert tag.name == tag_data["name"]
    assert tag.metadata == tag_data["metadata"]
    assert tag.parent_id == tag_data["parent_id"]


def test_tag_format_validation():
    """Test tag format validation rules"""
    # Arrange
    now = datetime.now(timezone.utc)
    base_data = {"id": uuid.uuid4(), "created_at": now, "updated_at": now}

    # Act & Assert - Valid formats
    valid_names = ["system.test", "system.category.subcategory", "system.test-tag"]

    for name in valid_names:
        tag = Tag(**{**base_data, "name": name})
        assert tag.name == name

    # Act & Assert - Invalid formats
    invalid_names = [
        "",  # Empty
        "notprefix",  # Missing system prefix
        "system.",  # Empty segment
        "system.test.",  # Trailing dot
        "system.invalid#char",  # Invalid character
        "system." + "x" * 100,  # Too long
    ]

    for name in invalid_names:
        with pytest.raises(ValidationError):
            Tag(**{**base_data, "name": name})


def test_tag_hierarchy():
    """Test tag hierarchy validation"""
    # Arrange
    now = datetime.now(timezone.utc)
    parent_id = uuid.uuid4()
    base_data = {
        "id": uuid.uuid4(),
        "created_at": now,
        "updated_at": now,
        "name": "system.category.test",
    }

    # Act & Assert - Valid parent
    tag = Tag(**{**base_data, "parent_id": parent_id})
    assert tag.parent_id == parent_id

    # Act & Assert - Self-reference
    with pytest.raises(ValidationError, match="Tag cannot reference itself as parent"):
        Tag(**{**base_data, "id": parent_id, "parent_id": parent_id})

    # Act & Assert - Optional parent
    tag = Tag(**base_data)
    assert tag.parent_id is None


def test_tag_metadata_validation():
    """Test tag metadata validation"""
    # Arrange
    now = datetime.now(timezone.utc)
    base_data = {
        "id": uuid.uuid4(),
        "created_at": now,
        "updated_at": now,
        "name": "system.category.test",
    }

    # Act & Assert - Valid metadata
    valid_metadata = {"description": "Test tag", "color": "#FF0000", "icon": "folder"}
    tag = Tag(**{**base_data, "metadata": valid_metadata})
    assert tag.metadata == valid_metadata

    # Act & Assert - Invalid metadata (not a dict)
    with pytest.raises(ValidationError, match="Input should be a valid dictionary"):
        Tag(**{**base_data, "metadata": ["invalid"]})

    # Act & Assert - Default metadata
    tag = Tag(**base_data)
    assert tag.metadata == {}
