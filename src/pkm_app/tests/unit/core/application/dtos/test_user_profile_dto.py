import pytest
from pydantic import ValidationError
from datetime import datetime, timezone
import uuid
from typing import Dict, Any

# Import DTOs from the new specific module
from pkm_app.core.application.dtos.user_profile_dto import (
    UserProfileBase,
    UserProfileCreate,
    UserProfileUpdate,
    UserProfileSchema,
)

# --- Helper Functions and Data (Copied from original test_dtos.py) ---


def get_utc_now() -> datetime:
    return datetime.now(timezone.utc)


VALID_USER_ID = "auth0|valid_user_id"
VALID_EMAIL = "test@example.com"


class MockOrmObject:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


# --- UserProfile DTO Tests ---


class TestUserProfileDTOs:
    def test_user_profile_base_creation_full(self):
        data = {
            "name": "Test User",
            "email": VALID_EMAIL,
            "preferences": {"theme": "dark"},
            "learned_context": {"last_login": str(get_utc_now())},
        }
        dto = UserProfileBase(**data)
        assert dto.name == data["name"]
        assert dto.email == data["email"]
        assert dto.preferences == data["preferences"]
        assert dto.learned_context == data["learned_context"]
        # Test extra fields forbidden
        with pytest.raises(ValidationError):
            UserProfileBase(**data, extra_field="should_fail")

    def test_user_profile_base_creation_minimal(self):
        dto = UserProfileBase()
        assert dto.name is None
        assert dto.email is None
        assert dto.preferences is None  # Default factory
        assert dto.learned_context == {}  # Default factory

    def test_user_profile_create_creation(self):
        data = {"user_id": VALID_USER_ID, "name": "New User", "email": "newuser@example.com"}
        dto = UserProfileCreate(**data)
        assert dto.user_id == data["user_id"]
        assert dto.name == data["name"]
        assert dto.email == data["email"]
        assert dto.preferences is None
        # Test extra fields forbidden
        with pytest.raises(ValidationError):
            UserProfileCreate(**data, extra_field="should_fail")

    def test_user_profile_create_missing_user_id(self):
        with pytest.raises(ValidationError) as excinfo:
            UserProfileCreate(name="Test")
        assert "user_id" in str(excinfo.value).lower()
        assert "field required" in str(excinfo.value).lower()

    def test_user_profile_update_creation(self):
        data = {"name": "Updated Name", "preferences": {"lang": "es"}}
        dto = UserProfileUpdate(**data)
        assert dto.name == data["name"]
        assert dto.email is None
        assert dto.preferences == data["preferences"]
        # Test extra fields forbidden
        with pytest.raises(ValidationError):
            UserProfileUpdate(**data, extra_field="should_fail")

    def test_user_profile_schema_creation_from_attributes(self):
        now = get_utc_now()
        mock_orm = MockOrmObject(
            user_id=VALID_USER_ID,
            name="ORM User",
            email="orm@example.com",
            preferences={"notifications": True},
            learned_context={"history": []},
            created_at=now,
            updated_at=now,
        )
        dto = UserProfileSchema.model_validate(mock_orm)
        assert dto.user_id == mock_orm.user_id
        assert dto.name == mock_orm.name
        assert dto.email == mock_orm.email
        assert dto.preferences == mock_orm.preferences
        assert dto.learned_context == mock_orm.learned_context
        assert dto.created_at == mock_orm.created_at
        assert dto.updated_at == mock_orm.updated_at
        # Test immutability (frozen=True)
        with pytest.raises(
            ValidationError
        ):  # Pydantic v2 raises ValidationError on attempt to change frozen model
            dto.name = "Cannot change"
        # Test extra fields forbidden (implicit via from_attributes and model_config)
        mock_orm_extra = MockOrmObject(**vars(mock_orm), extra_field="should_not_be_here")
        # model_validate will ignore extra fields if not in schema
        dto_extra_test = UserProfileSchema.model_validate(mock_orm_extra)
        assert not hasattr(dto_extra_test, "extra_field")

    def test_user_profile_invalid_email(self):
        with pytest.raises(ValidationError) as excinfo:
            UserProfileBase(email="invalid-email")
        assert "value is not a valid email address" in str(excinfo.value).lower()

    def test_user_profile_serialization_deserialization(self):
        now = get_utc_now()
        data = {
            "user_id": VALID_USER_ID,
            "name": "Serializable User",
            "email": "serial@example.com",
            "preferences": {"show_tips": False},
            "learned_context": {},  # Ensure it's an empty dict if None was intended for default_factory
            "created_at": now,
            "updated_at": now,
        }
        original_dto = UserProfileSchema(**data)
        dumped_data = original_dto.model_dump()

        # Pydantic v2 serializes datetime to string by default.
        # For comparison, ensure they are in the same format or re-parse.
        # model_validate can handle string dates.
        new_dto = UserProfileSchema.model_validate(dumped_data)
        assert new_dto == original_dto
        assert new_dto.learned_context == {}  # Check default factory behavior on deserialization
