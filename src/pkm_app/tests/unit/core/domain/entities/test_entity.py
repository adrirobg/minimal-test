"""Tests for the base Entity class"""

import uuid
from datetime import datetime, timezone
import pytest
from pydantic import ValidationError
from pkm_app.core.domain.entities.entity import Entity


class ConcreteEntity(Entity):
    """Concrete implementation of Entity for testing"""

    pass


def test_entity_base_fields():
    """Test basic entity field validation"""
    # Arrange
    entity_id = uuid.uuid4()
    now = datetime.now(timezone.utc)

    # Act
    entity = ConcreteEntity(id=entity_id, created_at=now, updated_at=now)

    # Assert
    assert entity.id == entity_id
    assert entity.created_at == now
    assert entity.updated_at == now

    # Verify immutability
    with pytest.raises(ValidationError):
        entity.id = uuid.uuid4()


def test_entity_id_validation():
    """Test validation of entity ID field"""
    # Arrange
    now = datetime.now(timezone.utc)
    invalid_id = "not-a-uuid"

    # Act & Assert
    with pytest.raises(ValidationError, match="Input should be a valid UUID"):
        ConcreteEntity(id=invalid_id, created_at=now, updated_at=now)


def test_entity_timestamp_validation():
    """Test validation of timestamp fields"""
    # Arrange
    entity_id = uuid.uuid4()
    naive_datetime = datetime.now()  # Naive datetime without timezone

    # Act & Assert - Test created_at validation
    with pytest.raises(ValidationError, match="timezone-aware datetime"):
        ConcreteEntity(
            id=entity_id, created_at=naive_datetime, updated_at=datetime.now(timezone.utc)
        )

    # Act & Assert - Test updated_at validation
    with pytest.raises(ValidationError, match="timezone-aware datetime"):
        ConcreteEntity(
            id=entity_id, created_at=datetime.now(timezone.utc), updated_at=naive_datetime
        )
