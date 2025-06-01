"""Tests for the UserProfile entity"""

import uuid
from datetime import datetime, timezone
import pytest
from pydantic import ValidationError
from pkm_app.core.domain.entities.user_profile import UserProfile


def test_userprofile_creation_valid():
    """Test creating a valid user profile"""
    # Arrange
    now = datetime.now(timezone.utc)
    profile_data = {
        "id": uuid.uuid4(),
        "created_at": now,
        "updated_at": now,
        "username": "testuser",
        "email": "test@example.com",
        "display_name": "Test User",
        "preferences": {"theme": "light", "language": "en", "notifications_enabled": True},
    }

    # Act
    profile = UserProfile(**profile_data)

    # Assert
    assert profile.id == profile_data["id"]
    assert profile.username == profile_data["username"]
    assert profile.email == profile_data["email"]
    assert profile.display_name == profile_data["display_name"]
    assert profile.preferences == profile_data["preferences"]


def test_userprofile_field_validation():
    """Test validation of user profile fields"""
    # Arrange
    now = datetime.now(timezone.utc)
    base_data = {"id": uuid.uuid4(), "created_at": now, "updated_at": now}

    # Act & Assert - Username validation
    invalid_usernames = ["", "a", "ab", "user@name", "user name", "a" * 51]
    for username in invalid_usernames:
        with pytest.raises(ValidationError):
            UserProfile(**{**base_data, "username": username, "email": "valid@example.com"})

    # Act & Assert - Email validation
    invalid_emails = ["", "notanemail", "@nodomain.com", "invalid@", "invalid@.com"]
    for email in invalid_emails:
        with pytest.raises(ValidationError):
            UserProfile(**{**base_data, "username": "validuser", "email": email})

    # Act & Assert - Display name validation
    with pytest.raises(ValidationError, match="String should have at most 100 characters"):
        UserProfile(
            **{
                **base_data,
                "username": "validuser",
                "email": "valid@example.com",
                "display_name": "x" * 101,
            }
        )


def test_userprofile_preferences():
    """Test user preferences validation"""
    # Arrange
    now = datetime.now(timezone.utc)
    base_data = {
        "id": uuid.uuid4(),
        "created_at": now,
        "updated_at": now,
        "username": "testuser",
        "email": "test@example.com",
    }

    # Act & Assert - Valid preferences
    valid_preferences = {
        "theme": "dark",
        "language": "es",
        "notifications_enabled": False,
        "custom_setting": "value",
    }
    profile = UserProfile(**{**base_data, "preferences": valid_preferences})
    assert profile.preferences == valid_preferences

    # Act & Assert - Default preferences
    profile = UserProfile(**base_data)
    assert profile.preferences == {}

    # Act & Assert - Invalid preferences (not a dict)
    with pytest.raises(ValidationError, match="Input should be a valid dictionary"):
        UserProfile(**{**base_data, "preferences": ["invalid"]})


def test_userprofile_email_format():
    """Test email format validation"""
    # Arrange
    now = datetime.now(timezone.utc)
    base_data = {"id": uuid.uuid4(), "created_at": now, "updated_at": now, "username": "testuser"}

    # Act & Assert - Valid emails
    valid_emails = ["test@example.com", "user.name@domain.com", "user+label@domain.co.uk"]
    for email in valid_emails:
        profile = UserProfile(**{**base_data, "email": email})
        assert str(profile.email) == email
