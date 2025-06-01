"""Tests for the Keyword entity"""

import uuid
from datetime import datetime, timezone
import pytest
from pydantic import ValidationError
from pkm_app.core.domain.entities.keyword import Keyword


def test_keyword_creation_valid():
    """Test creating a valid keyword"""
    # Arrange
    now = datetime.now(timezone.utc)
    keyword_data = {
        "id": uuid.uuid4(),
        "created_at": now,
        "updated_at": now,
        "name": "test-keyword",
        "user_id": uuid.uuid4(),
    }

    # Act
    keyword = Keyword(**keyword_data)

    # Assert
    assert keyword.id == keyword_data["id"]
    assert keyword.name == keyword_data["name"]
    assert keyword.user_id == keyword_data["user_id"]
    assert keyword.normalized_name == "test-keyword"


def test_keyword_name_validation():
    """Test keyword name validation rules"""
    # Arrange
    now = datetime.now(timezone.utc)
    base_data = {"id": uuid.uuid4(), "created_at": now, "updated_at": now, "user_id": uuid.uuid4()}

    # Act & Assert - Valid names
    valid_names = ["test", "test-keyword", "python3.9", "machine_learning"]
    for name in valid_names:
        keyword = Keyword(**{**base_data, "name": name})
        assert keyword.name == name

    # Act & Assert - Invalid names
    invalid_names = ["", " ", "a" * 101, "invalid@name", "no/slashes"]
    for name in invalid_names:
        with pytest.raises(ValidationError):
            Keyword(**{**base_data, "name": name})


def test_keyword_normalization():
    """Test keyword name normalization"""
    # Arrange
    now = datetime.now(timezone.utc)
    base_data = {"id": uuid.uuid4(), "created_at": now, "updated_at": now, "user_id": uuid.uuid4()}

    # Act & Assert - Test different formats
    test_cases = [
        ("Machine Learning", "machine-learning"),
        ("PYTHON3.9", "python3.9"),
        ("data_science", "data-science"),
        ("  spaces  ", "spaces"),
        ("multiple   spaces", "multiple-spaces"),
    ]

    for input_name, expected_normalized in test_cases:
        keyword = Keyword(**{**base_data, "name": input_name})
        assert keyword.normalized_name == expected_normalized
        assert keyword.name == input_name  # Original name should be preserved


def test_keyword_user_id_required():
    """Test that user_id is required"""
    # Arrange
    now = datetime.now(timezone.utc)
    keyword_data = {
        "id": uuid.uuid4(),
        "created_at": now,
        "updated_at": now,
        "name": "test-keyword",
    }

    # Act & Assert
    with pytest.raises(ValidationError, match="Field required"):
        Keyword(**keyword_data)
