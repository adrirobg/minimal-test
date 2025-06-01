import pytest
from pydantic import ValidationError
from datetime import datetime, timezone
import uuid

# Import DTOs from the new specific module
from pkm_app.core.application.dtos.keyword_dto import (
    KeywordBase,
    KeywordCreate,
    KeywordUpdate,
    KeywordSchema,
)

# --- Helper Functions and Data (Copied and adapted) ---


def get_utc_now() -> datetime:
    return datetime.now(timezone.utc)


VALID_USER_ID = "auth0|valid_user_id_keyword"
VALID_KEYWORD_UUID = uuid.uuid4()


class MockOrmObject:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


# --- Keyword DTO Tests ---


class TestKeywordDTOs:
    def test_keyword_base_creation(self):
        dto = KeywordBase(name="Python")
        assert dto.name == "Python"
        # Test extra fields forbidden
        with pytest.raises(ValidationError):
            KeywordBase(name="Python", extra_field="fail")

    def test_keyword_base_name_empty(self):
        with pytest.raises(ValidationError) as excinfo:
            KeywordBase(name="")
        assert "El nombre de la keyword no puede estar vacío." in str(excinfo.value)

    def test_keyword_base_name_whitespace(self):
        with pytest.raises(ValidationError) as excinfo:
            KeywordBase(name="   ")
        assert "El nombre de la keyword no puede estar vacío." in str(excinfo.value)

    def test_keyword_base_name_missing(self):
        with pytest.raises(ValidationError) as excinfo:
            KeywordBase()  # name is required
        assert "name" in str(excinfo.value).lower()
        assert "field required" in str(excinfo.value).lower()

    def test_keyword_create_creation(self):
        dto = KeywordCreate(name="FastAPI")
        assert dto.name == "FastAPI"
        # Test extra fields forbidden
        with pytest.raises(ValidationError):
            KeywordCreate(name="FastAPI", extra_field="fail")

    def test_keyword_update_creation(self):
        dto = KeywordUpdate(name="Pytest")
        assert dto.name == "Pytest"
        dto_none = KeywordUpdate()
        assert dto_none.name is None
        # Test extra fields forbidden
        with pytest.raises(ValidationError):
            KeywordUpdate(name="Pytest", extra_field="fail")

    def test_keyword_update_name_empty(self):
        with pytest.raises(ValidationError) as excinfo:
            KeywordUpdate(name="")
        assert "El nombre de la keyword no puede estar vacío." in str(excinfo.value)

    def test_keyword_update_name_whitespace(self):
        with pytest.raises(ValidationError) as excinfo:
            KeywordUpdate(name="   ")
        assert "El nombre de la keyword no puede estar vacío." in str(excinfo.value)

    def test_keyword_schema_creation_from_attributes(self):
        now = get_utc_now()
        mock_orm = MockOrmObject(
            id=VALID_KEYWORD_UUID, name="ORM Keyword", user_id=VALID_USER_ID, created_at=now
        )
        dto = KeywordSchema.model_validate(mock_orm)
        assert dto.id == mock_orm.id
        assert dto.name == mock_orm.name
        assert dto.user_id == mock_orm.user_id
        assert dto.created_at == mock_orm.created_at
        # Test immutability
        with pytest.raises(ValidationError):
            dto.name = "Cannot change"
        # Test extra fields (model_validate ignores them if not in schema)
        mock_orm_extra = MockOrmObject(**vars(mock_orm), extra_field="ignored")
        dto_extra_test = KeywordSchema.model_validate(mock_orm_extra)
        assert not hasattr(dto_extra_test, "extra_field")

    def test_keyword_schema_missing_fields(self):
        # Test missing id
        with pytest.raises(ValidationError):
            KeywordSchema(name="test", user_id=VALID_USER_ID, created_at=get_utc_now())
        # Test missing user_id
        with pytest.raises(ValidationError):
            KeywordSchema(name="test", id=VALID_KEYWORD_UUID, created_at=get_utc_now())
        # Test missing created_at
        with pytest.raises(ValidationError):
            KeywordSchema(name="test", id=VALID_KEYWORD_UUID, user_id=VALID_USER_ID)

    def test_keyword_serialization_deserialization(self):
        now = get_utc_now()
        data = {
            "id": VALID_KEYWORD_UUID,
            "name": "Serializable Keyword",
            "user_id": VALID_USER_ID,
            "created_at": now,
        }
        original_dto = KeywordSchema(**data)
        dumped_data = original_dto.model_dump()

        # Pydantic v2 handles UUID and datetime string conversion automatically on validation
        new_dto = KeywordSchema.model_validate(dumped_data)
        assert new_dto == original_dto
