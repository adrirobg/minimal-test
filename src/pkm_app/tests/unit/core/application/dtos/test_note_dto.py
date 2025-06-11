import pytest
from pydantic import ValidationError, AnyUrl
from datetime import datetime, timezone
import uuid
from typing import Dict, Any, List

# Import DTOs from the new specific modules
from pkm_app.core.application.dtos.note_dto import (
    NoteBase,
    NoteCreate,
    NoteUpdate,
    NoteSchema,
    NoteWithLinksSchema,
)
from pkm_app.core.application.dtos.project_dto import ProjectSchema
from pkm_app.core.application.dtos.source_dto import SourceSchema
from pkm_app.core.application.dtos.keyword_dto import KeywordSchema
from pkm_app.core.application.dtos.note_link_dto import NoteLinkSchema

# --- Helper Functions and Data (Copied and adapted) ---


def get_utc_now() -> datetime:
    return datetime.now(timezone.utc)


VALID_USER_ID = "auth0|valid_user_id_note"
VALID_NOTE_UUID = uuid.uuid4()
VALID_PROJECT_UUID_FOR_NOTE = uuid.uuid4()
VALID_SOURCE_UUID_FOR_NOTE = uuid.uuid4()
VALID_KEYWORD_UUID_FOR_NOTE = uuid.uuid4()
VALID_LINK_UUID_FOR_NOTE_SOURCE = uuid.uuid4()
VALID_LINK_UUID_FOR_NOTE_TARGET = uuid.uuid4()
ANOTHER_NOTE_UUID = uuid.uuid4()


class MockOrmObject:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


# --- Note DTO Tests ---


class TestNoteDTOs:
    def test_note_base_creation_full(self):
        data = {
            "title": "My Note",
            "content": "This is the content of the note.",
            "type": "personal_reflection",
            "note_metadata": {"mood": "happy"},
            "project_id": VALID_PROJECT_UUID_FOR_NOTE,
            "source_id": VALID_SOURCE_UUID_FOR_NOTE,
        }
        dto = NoteBase(**data)
        assert dto.title == data["title"]
        assert dto.content == data["content"]
        assert dto.type == data["type"]
        assert dto.note_metadata == data["note_metadata"]
        assert dto.project_id == data["project_id"]
        assert dto.source_id == data["source_id"]
        # Test extra fields forbidden
        with pytest.raises(ValidationError):
            NoteBase(**data, extra_field="fail")

    def test_note_base_creation_minimal_content_only(self):
        dto = NoteBase(content="Minimal content.")
        assert dto.content == "Minimal content."
        assert dto.title is None
        assert dto.type is None
        assert dto.project_id is None
        assert dto.source_id is None
        assert dto.note_metadata == {}  # Default factory

    def test_note_base_missing_content(self):
        with pytest.raises(ValidationError) as excinfo:
            NoteBase(title="Note without content")
        assert "content" in str(excinfo.value).lower()
        assert "field required" in str(excinfo.value).lower()

    def test_note_base_type_too_long(self):
        with pytest.raises(ValidationError) as excinfo:
            NoteBase(content="Valid content", type="a" * 101)
        assert "string should have at most 100 characters" in str(excinfo.value).lower()

    def test_note_create_creation(self):
        dto = NoteCreate(content="Content for new note.", title="New Note Title")
        assert dto.content == "Content for new note."
        assert dto.title == "New Note Title"
        # Test extra fields forbidden
        with pytest.raises(ValidationError):
            NoteCreate(content="Fail", extra_field="fail")

    def test_note_update_creation(self):
        dto = NoteUpdate(title="Updated Note Title", note_metadata={"status": "revised"})
        assert dto.title == "Updated Note Title"
        assert dto.content is None
        assert dto.note_metadata == {"status": "revised"}
        # Test extra fields forbidden
        with pytest.raises(ValidationError):
            NoteUpdate(title="Fail", extra_field="fail")

    def test_note_schema_creation_from_attributes(self):
        now = get_utc_now()
        project_orm = MockOrmObject(
            id=VALID_PROJECT_UUID_FOR_NOTE,
            name="Associated Project",
            user_id=VALID_USER_ID,
            created_at=now,
            updated_at=now,
        )
        source_orm = MockOrmObject(
            id=VALID_SOURCE_UUID_FOR_NOTE,
            title="Associated Source",
            user_id=VALID_USER_ID,
            created_at=now,
            updated_at=now,
            url=AnyUrl("http://source.com"),
        )
        keyword_orm = MockOrmObject(
            id=VALID_KEYWORD_UUID_FOR_NOTE, name="Tag1", user_id=VALID_USER_ID, created_at=now
        )

        mock_note_orm = MockOrmObject(
            id=VALID_NOTE_UUID,
            user_id=VALID_USER_ID,
            title="ORM Note",
            content="Content from ORM",
            type="technical",
            note_metadata={"version": 1},
            project_id=VALID_PROJECT_UUID_FOR_NOTE,
            source_id=VALID_SOURCE_UUID_FOR_NOTE,
            created_at=now,
            updated_at=now,
            project=project_orm,  # Populated by SQLAlchemy relationship
            source=source_orm,  # Populated by SQLAlchemy relationship
            keywords=[keyword_orm],  # Populated by SQLAlchemy relationship
        )

        dto = NoteSchema.model_validate(mock_note_orm)
        assert dto.id == mock_note_orm.id
        assert dto.user_id == mock_note_orm.user_id
        assert dto.title == mock_note_orm.title
        assert dto.content == mock_note_orm.content
        assert dto.project is not None
        assert dto.project.id == VALID_PROJECT_UUID_FOR_NOTE
        assert dto.source is not None
        assert dto.source.id == VALID_SOURCE_UUID_FOR_NOTE
        assert len(dto.keywords) == 1
        assert dto.keywords[0].id == VALID_KEYWORD_UUID_FOR_NOTE
        # Test immutability
        with pytest.raises(ValidationError):
            dto.title = "Cannot change"
        # Test extra fields
        mock_orm_extra = MockOrmObject(**vars(mock_note_orm), extra_field="ignored")
        dto_extra_test = NoteSchema.model_validate(mock_orm_extra)
        assert not hasattr(dto_extra_test, "extra_field")

    def test_note_schema_serialization_deserialization(self):
        now = get_utc_now()
        project_data = {
            "id": VALID_PROJECT_UUID_FOR_NOTE,
            "name": "Proj",
            "user_id": VALID_USER_ID,
            "created_at": now,
            "updated_at": now,
        }
        source_data = {
            "id": VALID_SOURCE_UUID_FOR_NOTE,
            "title": "Src",
            "user_id": VALID_USER_ID,
            "created_at": now,
            "updated_at": now,
            "url": AnyUrl("http://s.com"),
        }
        keyword_data = {
            "id": VALID_KEYWORD_UUID_FOR_NOTE,
            "name": "Key",
            "user_id": VALID_USER_ID,
            "created_at": now,
        }

        data = {
            "id": VALID_NOTE_UUID,
            "user_id": VALID_USER_ID,
            "title": "Serializable Note",
            "content": "Serializable content",
            "type": "meeting",
            "note_metadata": {"attendees": 5},
            "project_id": VALID_PROJECT_UUID_FOR_NOTE,
            "source_id": VALID_SOURCE_UUID_FOR_NOTE,
            "created_at": now,
            "updated_at": now,
            "project": ProjectSchema(**project_data),
            "source": SourceSchema(**source_data),
            "keywords": [KeywordSchema(**keyword_data)],
        }
        original_dto = NoteSchema(**data)
        dumped_data = original_dto.model_dump()
        new_dto = NoteSchema.model_validate(dumped_data)
        assert new_dto == original_dto
        assert new_dto.project.name == "Proj"
        assert len(new_dto.keywords) == 1

    def test_note_with_links_schema_creation_from_attributes(self):
        now = get_utc_now()
        link_source_orm = MockOrmObject(
            id=VALID_LINK_UUID_FOR_NOTE_SOURCE,
            source_note_id=VALID_NOTE_UUID,
            target_note_id=ANOTHER_NOTE_UUID,
            user_id=VALID_USER_ID,
            created_at=now,
            link_type="links_to",
        )
        link_target_orm = MockOrmObject(
            id=VALID_LINK_UUID_FOR_NOTE_TARGET,
            source_note_id=ANOTHER_NOTE_UUID,
            target_note_id=VALID_NOTE_UUID,
            user_id=VALID_USER_ID,
            created_at=now,
            link_type="linked_from",
        )

        mock_note_orm = MockOrmObject(
            id=VALID_NOTE_UUID,
            user_id=VALID_USER_ID,
            title="Note With Links",
            content="Content",
            created_at=now,
            updated_at=now,
            project=None,
            source=None,
            keywords=[],
            note_metadata={},
            project_id=None,
            source_id=None,
            type=None,
            source_of_links=[link_source_orm],  # Populated by SQLAlchemy relationship
            target_of_links=[link_target_orm],  # Populated by SQLAlchemy relationship
        )
        dto = NoteWithLinksSchema.model_validate(mock_note_orm)
        assert dto.id == VALID_NOTE_UUID
        assert len(dto.source_of_links) == 1
        assert dto.source_of_links[0].id == VALID_LINK_UUID_FOR_NOTE_SOURCE
        assert len(dto.target_of_links) == 1
        assert dto.target_of_links[0].id == VALID_LINK_UUID_FOR_NOTE_TARGET
        # Test immutability
        with pytest.raises(ValidationError):
            dto.title = "Cannot change"

    def test_note_with_links_schema_serialization_deserialization(self):
        now = get_utc_now()
        link1_data = {
            "id": uuid.uuid4(),
            "source_note_id": VALID_NOTE_UUID,
            "target_note_id": uuid.uuid4(),
            "user_id": VALID_USER_ID,
            "created_at": now,
            "link_type": "rel",
        }
        link2_data = {
            "id": uuid.uuid4(),
            "source_note_id": uuid.uuid4(),
            "target_note_id": VALID_NOTE_UUID,
            "user_id": VALID_USER_ID,
            "created_at": now,
            "link_type": "dep",
        }

        data = {
            "id": VALID_NOTE_UUID,
            "user_id": VALID_USER_ID,
            "title": "Note Links Test",
            "content": "Content",
            "created_at": now,
            "updated_at": now,
            "project": None,
            "source": None,
            "keywords": [],
            "note_metadata": {},
            "project_id": None,
            "source_id": None,
            "type": None,
            "source_of_links": [NoteLinkSchema(**link1_data)],
            "target_of_links": [NoteLinkSchema(**link2_data)],
        }
        original_dto = NoteWithLinksSchema(**data)
        dumped_data = original_dto.model_dump()
        new_dto = NoteWithLinksSchema.model_validate(dumped_data)
        assert new_dto == original_dto
        assert len(new_dto.source_of_links) == 1
        assert len(new_dto.target_of_links) == 1
