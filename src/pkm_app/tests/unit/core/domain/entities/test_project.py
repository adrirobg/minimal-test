"""Tests for the Project entity"""

import uuid
from datetime import datetime, timezone
import pytest
from pydantic import ValidationError
from pkm_app.core.domain.entities.project import Project


def test_project_creation_valid():
    """Test creating a valid project"""
    # Arrange
    now = datetime.now(timezone.utc)
    project_data = {
        "id": uuid.uuid4(),
        "created_at": now,
        "updated_at": now,
        "name": "Test Project",
        "description": "A test project description",
        "status": "active",
        "metadata": {"priority": 1, "category": "research"},
    }

    # Act
    project = Project(**project_data)

    # Assert
    assert project.id == project_data["id"]
    assert project.name == project_data["name"]
    assert project.description == project_data["description"]
    assert project.status == project_data["status"]
    assert project.metadata == project_data["metadata"]


def test_project_name_description_validation():
    """Test project name and description validation"""
    # Arrange
    now = datetime.now(timezone.utc)
    base_data = {"id": uuid.uuid4(), "created_at": now, "updated_at": now, "status": "active"}

    # Act & Assert - Name validation
    # Test empty name
    with pytest.raises(ValidationError, match="String should have at least 1 character"):
        Project(**{**base_data, "name": "", "description": "Valid description"})

    # Test too long name
    with pytest.raises(ValidationError, match="String should have at most 100 characters"):
        Project(**{**base_data, "name": "x" * 101, "description": "Valid description"})

    # Test name with invalid characters
    with pytest.raises(ValidationError):
        Project(**{**base_data, "name": "Invalid/Name", "description": "Valid description"})

    # Act & Assert - Description validation
    # Test too long description
    with pytest.raises(ValidationError, match="String should have at most 500 characters"):
        Project(**{**base_data, "name": "Valid Name", "description": "x" * 501})

    # Test valid case with optional description
    project = Project(**{**base_data, "name": "Valid Name"})
    assert project.description == ""


def test_project_status():
    """Test project status validation"""
    # Arrange
    now = datetime.now(timezone.utc)
    base_data = {"id": uuid.uuid4(), "created_at": now, "updated_at": now, "name": "Test Project"}

    # Act & Assert - Valid statuses
    valid_statuses = ["active", "completed", "archived", "on_hold"]
    for status in valid_statuses:
        project = Project(**{**base_data, "status": status})
        assert project.status == status

    # Act & Assert - Invalid status
    with pytest.raises(ValidationError, match="Invalid project status"):
        Project(**{**base_data, "status": "invalid_status"})

    # Act & Assert - Default status
    project = Project(**{k: v for k, v in base_data.items() if k != "status"})
    assert project.status == "active"


def test_project_metadata_validation():
    """Test project metadata validation"""
    # Arrange
    now = datetime.now(timezone.utc)
    base_data = {
        "id": uuid.uuid4(),
        "created_at": now,
        "updated_at": now,
        "name": "Test Project",
        "status": "active",
    }

    # Act & Assert - Valid metadata
    valid_metadata = {"priority": 1, "category": "research", "tags": ["test", "project"]}
    project = Project(**{**base_data, "metadata": valid_metadata})
    assert project.metadata == valid_metadata

    # Act & Assert - Invalid metadata (not a dict)
    with pytest.raises(ValidationError, match="Input should be a valid dictionary"):
        Project(**{**base_data, "metadata": ["invalid"]})

    # Act & Assert - Default metadata
    project = Project(**base_data)
    assert project.metadata == {}
