import pytest
from pydantic import ValidationError
from datetime import datetime, timezone
import uuid

# Import DTOs from the new specific module
from pkm_app.core.application.dtos.note_link_dto import (
    NoteLinkBase,
    NoteLinkCreate,
    NoteLinkUpdate,
    NoteLinkSchema,
)

# --- Helper Functions and Data (Copied and adapted) ---


def get_utc_now() -> datetime:
    return datetime.now(timezone.utc)


VALID_USER_ID = "auth0|valid_user_id_notelink"
VALID_NOTE_LINK_UUID = uuid.uuid4()
VALID_SOURCE_NOTE_UUID = uuid.uuid4()
VALID_TARGET_NOTE_UUID = uuid.uuid4()


class MockOrmObject:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


# --- NoteLink DTO Tests ---


class TestNoteLinkDTOs:
    def test_note_link_base_creation_full(self):
        dto = NoteLinkBase(link_type="connects_to", description="Specific connection")
        assert dto.link_type == "connects_to"
        assert dto.description == "Specific connection"
        # Test extra fields forbidden
        with pytest.raises(ValidationError):
            NoteLinkBase(link_type="fail", extra_field="fail")

    def test_note_link_base_creation_default_link_type(self):
        dto = NoteLinkBase()
        assert dto.link_type == "related"  # Default value from DTO definition
        assert dto.description is None

    def test_note_link_base_link_type_too_long(self):
        with pytest.raises(ValidationError) as excinfo:
            NoteLinkBase(link_type="a" * 101)
        assert "string should have at most 100 characters" in str(excinfo.value).lower()

    def test_note_link_create_creation(self):
        dto = NoteLinkCreate(
            source_note_id=VALID_SOURCE_NOTE_UUID, target_note_id=VALID_TARGET_NOTE_UUID
        )
        assert dto.source_note_id == VALID_SOURCE_NOTE_UUID
        assert dto.target_note_id == VALID_TARGET_NOTE_UUID
        assert dto.link_type == "related"  # Default from NoteLinkBase
        # Test extra fields forbidden
        with pytest.raises(ValidationError):
            NoteLinkCreate(
                source_note_id=uuid.uuid4(), target_note_id=uuid.uuid4(), extra_field="fail"
            )

    def test_note_link_create_missing_ids(self):
        with pytest.raises(ValidationError) as excinfo_source:
            NoteLinkCreate(target_note_id=VALID_TARGET_NOTE_UUID)
        assert "source_note_id" in str(excinfo_source.value).lower()
        assert "field required" in str(excinfo_source.value).lower()

        with pytest.raises(ValidationError) as excinfo_target:
            NoteLinkCreate(source_note_id=VALID_SOURCE_NOTE_UUID)
        assert "target_note_id" in str(excinfo_target.value).lower()
        assert "field required" in str(excinfo_target.value).lower()

    def test_note_link_update_creation(self):
        dto = NoteLinkUpdate(link_type="updated_link")
        assert dto.link_type == "updated_link"
        assert dto.description is None
        # Test extra fields forbidden
        with pytest.raises(ValidationError):
            NoteLinkUpdate(link_type="fail", extra_field="fail")

    def test_note_link_schema_creation_from_attributes(self):
        now = get_utc_now()
        mock_orm = MockOrmObject(
            id=VALID_NOTE_LINK_UUID,
            source_note_id=VALID_SOURCE_NOTE_UUID,
            target_note_id=VALID_TARGET_NOTE_UUID,
            user_id=VALID_USER_ID,
            link_type="orm_link",
            created_at=now,
            description="From ORM",
        )
        dto = NoteLinkSchema.model_validate(mock_orm)
        assert dto.id == mock_orm.id
        assert dto.source_note_id == mock_orm.source_note_id
        assert dto.target_note_id == mock_orm.target_note_id
        assert dto.user_id == mock_orm.user_id
        assert dto.link_type == mock_orm.link_type
        assert dto.created_at == mock_orm.created_at
        assert dto.description == "From ORM"
        # Test immutability
        with pytest.raises(ValidationError):
            dto.link_type = "Cannot change"
        # Test extra fields
        mock_orm_extra = MockOrmObject(**vars(mock_orm), extra_field="ignored")
        dto_extra_test = NoteLinkSchema.model_validate(mock_orm_extra)
        assert not hasattr(dto_extra_test, "extra_field")

    def test_note_link_serialization_deserialization(self):
        now = get_utc_now()
        data = {
            "id": VALID_NOTE_LINK_UUID,
            "source_note_id": VALID_SOURCE_NOTE_UUID,
            "target_note_id": VALID_TARGET_NOTE_UUID,
            "user_id": VALID_USER_ID,
            "link_type": "serial_link",
            "description": "Serializable link",
            "created_at": now,
        }
        original_dto = NoteLinkSchema(**data)
        dumped_data = original_dto.model_dump()

        new_dto = NoteLinkSchema.model_validate(dumped_data)
        assert new_dto == original_dto
