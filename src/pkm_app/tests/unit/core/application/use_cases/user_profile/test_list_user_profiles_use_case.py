"""Unit tests for the ListUserProfilesUseCase."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from datetime import datetime, timezone

from pkm_app.core.application.dtos.user_profile_dto import UserProfileDTO
from pkm_app.core.application.use_cases.user_profile.list_user_profiles_use_case import (
    ListUserProfilesUseCase,
)
from pkm_app.core.application.interfaces.user_profile_interface import IUserProfileRepository
from pkm_app.core.domain.entities.user_profile import UserProfile


@pytest.fixture
def mock_user_profile_repository():
    """Fixture for a mocked IUserProfileRepository."""
    mock = AsyncMock(spec=IUserProfileRepository)
    mock.list_all = AsyncMock()
    mock.get_all = AsyncMock()
    mock.get_by_id = AsyncMock()
    mock.get_by_email = AsyncMock()
    mock.exists = AsyncMock()
    mock.add = AsyncMock()
    mock.delete = AsyncMock()
    mock.update = AsyncMock()
    return mock


@pytest.fixture
def list_user_profiles_use_case(mock_user_profile_repository):
    """Fixture for the ListUserProfilesUseCase."""
    return ListUserProfilesUseCase(mock_user_profile_repository)


@pytest.mark.asyncio
async def test_list_all_user_profiles(
    list_user_profiles_use_case: ListUserProfilesUseCase, mock_user_profile_repository: AsyncMock
):
    """Test listing all user profiles when multiple exist."""
    profile1 = UserProfile(
        id=uuid4(),
        username="user1",
        email="user1@example.com",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    profile2 = UserProfile(
        id=uuid4(),
        username="user2",
        email="user2@example.com",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    mock_user_profile_repository.list_all.return_value = [profile1, profile2]

    result_dtos = await list_user_profiles_use_case.execute()

    mock_user_profile_repository.list_all.assert_called_once_with(filters=None, offset=0, limit=100)
    assert len(result_dtos) == 2
    assert isinstance(result_dtos[0], UserProfileDTO)
    assert isinstance(result_dtos[1], UserProfileDTO)
    assert result_dtos[0].id == profile1.id
    assert result_dtos[1].username == profile2.username


@pytest.mark.asyncio
async def test_list_user_profiles_empty(
    list_user_profiles_use_case: ListUserProfilesUseCase, mock_user_profile_repository: AsyncMock
):
    """Test listing user profiles when none exist."""
    mock_user_profile_repository.list_all.return_value = []

    result_dtos = await list_user_profiles_use_case.execute()

    mock_user_profile_repository.list_all.assert_called_once_with(filters=None, offset=0, limit=100)
    assert len(result_dtos) == 0


@pytest.mark.asyncio
async def test_list_user_profiles_with_filters_pagination(
    list_user_profiles_use_case: ListUserProfilesUseCase, mock_user_profile_repository: AsyncMock
):
    """Test listing user profiles with filters and pagination."""
    profile1 = UserProfile(
        id=uuid4(),
        username="filtered_user",
        email="filter@example.com",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    mock_user_profile_repository.list_all.return_value = [profile1]

    filters = {"username_contains": "filtered"}
    offset = 5
    limit = 10

    result_dtos = await list_user_profiles_use_case.execute(
        filters=filters, offset=offset, limit=limit
    )

    mock_user_profile_repository.list_all.assert_called_once_with(
        filters=filters, offset=offset, limit=limit
    )
    assert len(result_dtos) == 1
    assert result_dtos[0].username == "filtered_user"


@pytest.mark.asyncio
async def test_list_user_profiles_repository_general_exception(
    list_user_profiles_use_case: ListUserProfilesUseCase, mock_user_profile_repository: AsyncMock
):
    """Test handling of a generic exception from the repository."""
    mock_user_profile_repository.list_all.side_effect = Exception("Database query failed")

    with pytest.raises(Exception, match="Failed to list user profiles: Database query failed"):
        await list_user_profiles_use_case.execute()

    mock_user_profile_repository.list_all.assert_called_once_with(filters=None, offset=0, limit=100)


def test_list_user_profiles_use_case_invalid_repository_type():
    """Test ListUserProfilesUseCase init with invalid repository type."""
    with pytest.raises(
        TypeError, match="user_profile_repository must be an instance of IUserProfileRepository"
    ):
        ListUserProfilesUseCase(MagicMock())
