"""Unit tests for the GetUserProfileUseCase."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4, UUID
from datetime import datetime, timezone

from pkm_app.core.application.dtos.user_profile_dto import UserProfileDTO
from pkm_app.core.application.use_cases.user_profile.get_user_profile_use_case import (
    GetUserProfileUseCase,
)
from pkm_app.core.application.interfaces.user_profile_interface import IUserProfileRepository
from pkm_app.core.domain.entities.user_profile import UserProfile
from pkm_app.core.domain.errors import EntityNotFoundError


@pytest.fixture
def mock_user_profile_repository():
    """Fixture for a mocked IUserProfileRepository."""
    return AsyncMock(spec=IUserProfileRepository)


@pytest.fixture
def get_user_profile_use_case(mock_user_profile_repository):
    """Fixture for the GetUserProfileUseCase."""
    return GetUserProfileUseCase(mock_user_profile_repository)


@pytest.mark.asyncio
async def test_get_user_profile_existing_id(
    get_user_profile_use_case: GetUserProfileUseCase, mock_user_profile_repository: AsyncMock
):
    """Test retrieving an existing user profile by ID."""
    user_id = uuid4()
    expected_profile = UserProfile(
        id=user_id,
        username="testuser",
        email="test@example.com",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    mock_user_profile_repository.get_by_id.return_value = expected_profile

    retrieved_profile_dto = await get_user_profile_use_case.execute(user_id)

    mock_user_profile_repository.get_by_id.assert_called_once_with(user_id)
    assert retrieved_profile_dto is not None
    assert retrieved_profile_dto.id == user_id
    assert retrieved_profile_dto.username == "testuser"
    assert retrieved_profile_dto.email == "test@example.com"


@pytest.mark.asyncio
async def test_get_user_profile_non_existing_id(
    get_user_profile_use_case: GetUserProfileUseCase, mock_user_profile_repository: AsyncMock
):
    """Test retrieving a user profile with a non-existing ID."""
    non_existing_id = uuid4()
    mock_user_profile_repository.get_by_id.return_value = None

    with pytest.raises(
        EntityNotFoundError, match=f"User profile with ID '{non_existing_id}' not found."
    ):
        await get_user_profile_use_case.execute(non_existing_id)

    mock_user_profile_repository.get_by_id.assert_called_once_with(non_existing_id)


@pytest.mark.asyncio
async def test_get_user_profile_invalid_id_type(get_user_profile_use_case: GetUserProfileUseCase):
    """Test retrieving a user profile with an invalid ID type."""
    with pytest.raises(ValueError, match="user_profile_id must be a valid UUID."):
        await get_user_profile_use_case.execute("not-a-uuid")  # type: ignore


@pytest.mark.asyncio
async def test_get_user_profile_repository_general_exception(
    get_user_profile_use_case: GetUserProfileUseCase, mock_user_profile_repository: AsyncMock
):
    """Test handling of a generic exception from the repository."""
    user_id = uuid4()
    mock_user_profile_repository.get_by_id.side_effect = Exception("Database error")

    with pytest.raises(
        Exception, match=f"Failed to retrieve user profile {user_id}: Database error"
    ):
        await get_user_profile_use_case.execute(user_id)

    mock_user_profile_repository.get_by_id.assert_called_once_with(user_id)


def test_get_user_profile_use_case_invalid_repository_type():
    """Test GetUserProfileUseCase init with invalid repository type."""
    with pytest.raises(
        TypeError, match="user_profile_repository must be an instance of IUserProfileRepository"
    ):
        GetUserProfileUseCase(MagicMock())


# Note: The spec mentioned "Obtiene perfil por email".
# This functionality is not directly in the GetUserProfileUseCase as implemented,
# which strictly uses ID. If getting by email is required, it would typically be
# a separate use case (e.g., GetUserProfileByEmailUseCase) or an extension
# to the repository and this use case to handle different lookup strategies.
# For now, tests align with the current ID-based implementation.
