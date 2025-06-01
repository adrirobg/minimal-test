import pytest
from pydantic import ValidationError, AnyUrl
from datetime import datetime, timezone
import uuid
from typing import Dict, Any

# Import DTOs from the new specific module
from pkm_app.core.application.dtos.source_dto import (
    SourceBase,
    SourceCreate,
    SourceUpdate,
    SourceSchema,
)

# --- Helper Functions and Data (Copied and adapted) ---


def get_utc_now() -> datetime:
    return datetime.now(timezone.utc)


VALID_USER_ID = "auth0|valid_user_id_source"
VALID_SOURCE_UUID = uuid.uuid4()
VALID_URL = "http://example.com/article"
INVALID_URL = "notaurl"


class MockOrmObject:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


# --- Source DTO Tests ---


class TestSourceDTOs:
    def test_source_base_creation_full(self):
        data = {
            "type": "article",
            "title": "My Article",
            "description": "An interesting article.",
            "url": VALID_URL,
            "link_metadata": {"author": "John Doe"},
        }
        dto = SourceBase(**data)
        assert dto.type == data["type"]
        assert dto.title == data["title"]
        assert dto.description == data["description"]
        assert str(dto.url) == data["url"]  # AnyUrl needs to be cast to str for comparison
        assert dto.link_metadata == data["link_metadata"]
        # Test extra fields forbidden
        with pytest.raises(ValidationError):
            SourceBase(**data, extra_field="fail")

    def test_source_base_creation_minimal(self):
        dto = SourceBase()
        assert dto.type is None
        assert dto.title is None
        assert dto.url is None
        assert dto.link_metadata == {}  # Default factory

    def test_source_base_type_too_long(self):
        with pytest.raises(ValidationError) as excinfo:
            SourceBase(type="a" * 101)
        assert "string should have at most 100 characters" in str(excinfo.value).lower()

    def test_source_base_invalid_url(self):
        with pytest.raises(ValidationError) as excinfo:
            SourceBase(url=INVALID_URL)
        assert "url_parsing" in str(excinfo.value).lower()

    def test_source_create_creation(self):
        dto = SourceCreate(title="New Source", url="http://new.example.com")
        assert dto.title == "New Source"
        assert dto.url == AnyUrl("http://new.example.com")  # Compare AnyUrl objects
        # Test extra fields forbidden
        with pytest.raises(ValidationError):
            SourceCreate(title="Fail", url="http://f.com", extra_field="fail")

    def test_source_update_creation(self):
        dto = SourceUpdate(description="Updated source description")
        assert dto.description == "Updated source description"
        assert dto.title is None
        # Test extra fields forbidden
        with pytest.raises(ValidationError):
            SourceUpdate(description="Fail", extra_field="fail")

    def test_source_schema_creation_from_attributes(self):
        now = get_utc_now()
        mock_orm = MockOrmObject(
            id=VALID_SOURCE_UUID,
            user_id=VALID_USER_ID,
            type="book",
            title="ORM Book",
            url=str(AnyUrl("http://orm.example.com")),  # Store as string if ORM stores it as string
            created_at=now,
            updated_at=now,
            description=None,
            link_metadata=None,  # Test with None, should become {}
        )
        dto = SourceSchema.model_validate(mock_orm)
        assert dto.id == mock_orm.id
        assert dto.user_id == mock_orm.user_id
        assert dto.title == mock_orm.title
        assert str(dto.url) == mock_orm.url  # Mock ORM stores URL as string after AnyUrl conversion
        assert dto.created_at == mock_orm.created_at
        assert dto.link_metadata is None  # If ORM has None, DTO should have None
        # Test immutability
        with pytest.raises(ValidationError):
            dto.title = "Cannot change"
        # Test extra fields
        mock_orm_extra = MockOrmObject(**vars(mock_orm), extra_field="ignored")
        dto_extra_test = SourceSchema.model_validate(mock_orm_extra)
        assert not hasattr(dto_extra_test, "extra_field")

    def test_source_serialization_deserialization(self):
        now = get_utc_now()
        data = {
            "id": VALID_SOURCE_UUID,
            "user_id": VALID_USER_ID,
            "type": "website",
            "title": "Serializable Source",
            "url": AnyUrl("http://serial.example.com"),
            "created_at": now,
            "updated_at": now,
            "description": "A test description",
            "link_metadata": {"key": "value"},
        }
        original_dto = SourceSchema(**data)
        dumped_data = original_dto.model_dump()

        # AnyUrl is serialized to string, Pydantic handles re-parsing
        new_dto = SourceSchema.model_validate(dumped_data)
        assert new_dto == original_dto
        assert new_dto.description == data["description"]
        assert new_dto.link_metadata == data["link_metadata"]

    def test_source_serialization_deserialization_minimal_fields(self):
        now = get_utc_now()
        data_minimal = {
            "id": uuid.uuid4(),
            "user_id": VALID_USER_ID,
            "created_at": now,
            "updated_at": now,
            # type, title, url, description, link_metadata are None or default
        }
        original_dto_minimal = SourceSchema(**data_minimal)
        # Check defaults before dump
        assert original_dto_minimal.type is None
        assert original_dto_minimal.title is None
        assert original_dto_minimal.url is None
        assert original_dto_minimal.description is None
        assert original_dto_minimal.link_metadata == {}

        dumped_data_minimal = original_dto_minimal.model_dump(exclude_none=True)

        # Re-validate, Pydantic should apply defaults for missing fields
        new_dto_minimal = SourceSchema.model_validate(dumped_data_minimal)

        assert new_dto_minimal.id == original_dto_minimal.id
        assert new_dto_minimal.user_id == original_dto_minimal.user_id
        assert new_dto_minimal.type is None  # Default is None
        assert new_dto_minimal.title is None  # Default is None
        assert new_dto_minimal.url is None  # Default is None
        assert new_dto_minimal.description is None  # Default is None
        assert new_dto_minimal.link_metadata == {}  # Default factory
        assert new_dto_minimal.created_at == original_dto_minimal.created_at
        assert new_dto_minimal.updated_at == original_dto_minimal.updated_at
