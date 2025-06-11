import pytest
from pydantic import ValidationError
from datetime import datetime, timezone
import uuid

# Import DTOs from the new specific module
from pkm_app.core.application.dtos.project_dto import (
    ProjectBase,
    ProjectCreate,
    ProjectUpdate,
    ProjectSchema,
)

# --- Helper Functions and Data (Copied and adapted) ---


def get_utc_now() -> datetime:
    return datetime.now(timezone.utc)


VALID_USER_ID = "auth0|valid_user_id_project"
VALID_PROJECT_UUID = uuid.uuid4()
VALID_PARENT_PROJECT_UUID = uuid.uuid4()


class MockOrmObject:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


# --- Project DTO Tests ---


class TestProjectDTOs:
    def test_project_base_creation_full(self):
        dto = ProjectBase(
            name="Main Project",
            description="My main project",
            parent_project_id=VALID_PARENT_PROJECT_UUID,
        )
        assert dto.name == "Main Project"
        assert dto.description == "My main project"
        assert dto.parent_project_id == VALID_PARENT_PROJECT_UUID
        # Test extra fields forbidden
        with pytest.raises(ValidationError):
            ProjectBase(name="Fail", extra_field="fail")

    def test_project_base_creation_minimal(self):
        dto = ProjectBase(name="Sub Project")
        assert dto.name == "Sub Project"
        assert dto.description is None
        assert dto.parent_project_id is None

    def test_project_base_name_empty(self):
        with pytest.raises(ValidationError) as excinfo:
            ProjectBase(name="")
        assert "string should have at least 1 character" in str(excinfo.value).lower()

    def test_project_base_name_missing(self):
        with pytest.raises(ValidationError) as excinfo:
            ProjectBase(description="A project without a name")
        assert "name" in str(excinfo.value).lower()
        assert "field required" in str(excinfo.value).lower()

    def test_project_create_creation(self):
        dto = ProjectCreate(name="New Project Alpha")
        assert dto.name == "New Project Alpha"
        # Test extra fields forbidden
        with pytest.raises(ValidationError):
            ProjectCreate(name="Fail Create", extra_field="fail")

    def test_project_update_creation(self):
        dto = ProjectUpdate(description="Updated description")
        assert dto.name is None
        assert dto.description == "Updated description"
        # Test extra fields forbidden
        with pytest.raises(ValidationError):
            ProjectUpdate(description="Fail Update", extra_field="fail")

    def test_project_update_name_empty(self):
        with pytest.raises(ValidationError) as excinfo:
            ProjectUpdate(name="")
        assert "string should have at least 1 character" in str(excinfo.value).lower()

    def test_project_schema_creation_from_attributes(self):
        now = get_utc_now()
        mock_orm = MockOrmObject(
            id=VALID_PROJECT_UUID,
            name="ORM Project",
            description="From ORM",
            user_id=VALID_USER_ID,
            parent_project_id=None,
            created_at=now,
            updated_at=now,
        )
        dto = ProjectSchema.model_validate(mock_orm)
        assert dto.id == mock_orm.id
        assert dto.name == mock_orm.name
        assert dto.user_id == mock_orm.user_id
        assert dto.created_at == mock_orm.created_at
        assert dto.updated_at == mock_orm.updated_at
        assert dto.parent_project_id is None
        # Test immutability
        with pytest.raises(ValidationError):
            dto.name = "Cannot change"
        # Test extra fields (model_validate ignores them)
        mock_orm_extra = MockOrmObject(**vars(mock_orm), extra_field="ignored")
        dto_extra_test = ProjectSchema.model_validate(mock_orm_extra)
        assert not hasattr(dto_extra_test, "extra_field")

    def test_project_invalid_parent_id_type(self):
        with pytest.raises(ValidationError) as excinfo:
            ProjectBase(name="Test", parent_project_id="not-a-uuid")
        # Pydantic v2 gives a more generic error for UUID validation failure
        assert "uuid_parsing" in str(excinfo.value).lower()

    def test_project_serialization_deserialization(self):
        now = get_utc_now()
        data = {
            "id": VALID_PROJECT_UUID,
            "name": "Serializable Project",
            "description": "Test",
            "user_id": VALID_USER_ID,
            "parent_project_id": VALID_PARENT_PROJECT_UUID,  # Test with a parent ID
            "created_at": now,
            "updated_at": now,
        }
        original_dto = ProjectSchema(**data)
        dumped_data = original_dto.model_dump()

        new_dto = ProjectSchema.model_validate(dumped_data)
        assert new_dto == original_dto
        assert new_dto.parent_project_id == VALID_PARENT_PROJECT_UUID

    def test_project_serialization_deserialization_no_parent(self):
        now = get_utc_now()
        data_no_parent = {
            "id": uuid.uuid4(),
            "name": "Serializable Project No Parent",
            "description": "Test No Parent",
            "user_id": VALID_USER_ID,
            "parent_project_id": None,
            "created_at": now,
            "updated_at": now,
        }
        original_dto_no_parent = ProjectSchema(**data_no_parent)
        dumped_data_no_parent = original_dto_no_parent.model_dump()
        new_dto_no_parent = ProjectSchema.model_validate(dumped_data_no_parent)
        assert new_dto_no_parent == original_dto_no_parent
        assert new_dto_no_parent.parent_project_id is None
