"""Unit tests for the UpdateUserProfileUseCase."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4, UUID

from pkm_app.core.application.dtos.user_profile_dto import UserProfileDTO
from pkm_app.core.application.use_cases.user_profile.update_user_profile_use_case import (
    UpdateUserProfileUseCase,
)
from pkm_app.core.application.interfaces.user_profile_interface import IUserProfileRepository
from pkm_app.core.application.interfaces.unit_of_work_interface import IUnitOfWork
from pkm_app.core.domain.entities.user_profile import UserProfile
from pkm_app.core.domain.errors import EntityNotFoundError, DuplicateEntityError


@pytest.fixture
def mock_user_profile_repository():
    """Fixture for a mocked IUserProfileRepository."""
    mock = AsyncMock(spec=IUserProfileRepository)
    mock.get_by_id = AsyncMock()
    mock.update = AsyncMock()
    mock.get_by_email = AsyncMock()
    mock.exists = AsyncMock()
    mock.list_all = AsyncMock()
    mock.get_all = AsyncMock()
    mock.add = AsyncMock()
    mock.delete = AsyncMock()
    return mock


@pytest.fixture
def mock_unit_of_work():
    """Fixture for a mocked IUnitOfWork."""
    mock = AsyncMock(spec=IUnitOfWork)
    # Add begin method to mock
    mock.begin = AsyncMock()
    mock.begin.return_value.__aenter__.return_value = None
    mock.begin.return_value.__aexit__.return_value = None
    return mock


@pytest.fixture
def update_user_profile_use_case(mock_user_profile_repository, mock_unit_of_work):
    """Fixture for the UpdateUserProfileUseCase."""
    return UpdateUserProfileUseCase(mock_user_profile_repository, mock_unit_of_work)


@pytest.mark.asyncio
async def test_update_user_profile_valid_data(
    update_user_profile_use_case: UpdateUserProfileUseCase,
    mock_user_profile_repository: AsyncMock,
    mock_unit_of_work: AsyncMock,
):
    """Test updating a user profile with valid data."""
    user_id = uuid4()
    existing_profile = UserProfile(id=user_id, username="olduser", email="old@example.com")
    mock_user_profile_repository.get_by_id.return_value = existing_profile

    update_data = {"username": "newuser", "email": "new@example.com"}

    # Mock repository update to do nothing
    mock_user_profile_repository.update.return_value = None

    updated_profile_dto = await update_user_profile_use_case.execute(user_id, update_data)

    mock_user_profile_repository.get_by_id.assert_called_once_with(user_id)
    mock_user_profile_repository.update.assert_called_once()

    # Check that the argument to update is the modified UserProfile instance
    updated_profile_arg = mock_user_profile_repository.update.call_args[0][0]
    assert isinstance(updated_profile_arg, UserProfile)
    assert updated_profile_arg.id == user_id
    assert updated_profile_arg.username == "newuser"
    assert updated_profile_arg.email == "new@example.com"

    mock_unit_of_work.commit.assert_called_once()
    mock_unit_of_work.rollback.assert_not_called()

    assert updated_profile_dto is not None
    assert updated_profile_dto.id == user_id
    assert updated_profile_dto.username == "newuser"
    assert updated_profile_dto.email == "new@example.com"


@pytest.mark.asyncio
async def test_update_user_profile_non_existing_id(
    update_user_profile_use_case: UpdateUserProfileUseCase,
    mock_user_profile_repository: AsyncMock,
    mock_unit_of_work: AsyncMock,
):
    """Test updating a user profile with a non-existing ID."""
    non_existing_id = uuid4()
    mock_user_profile_repository.get_by_id.return_value = None
    update_data = {"username": "anyuser"}

    with pytest.raises(
        EntityNotFoundError, match=f"User profile with ID '{non_existing_id}' not found."
    ):
        await update_user_profile_use_case.execute(non_existing_id, update_data)

    mock_user_profile_repository.get_by_id.assert_called_once_with(non_existing_id)
    mock_user_profile_repository.update.assert_not_called()
    mock_unit_of_work.commit.assert_not_called()
    mock_unit_of_work.rollback.assert_called_once()


@pytest.mark.asyncio
async def test_update_user_profile_duplicate_email(
    update_user_profile_use_case: UpdateUserProfileUseCase,
    mock_user_profile_repository: AsyncMock,
    mock_unit_of_work: AsyncMock,
):
    """Test updating a user profile to an email that already exists."""
    user_id = uuid4()
    existing_profile = UserProfile(id=user_id, username="user1", email="user1@example.com")
    mock_user_profile_repository.get_by_id.return_value = existing_profile

    update_data = {"email": "duplicate@example.com"}
    mock_user_profile_repository.update.side_effect = DuplicateEntityError("Email already exists.")

    with pytest.raises(DuplicateEntityError, match="Email already exists."):
        await update_user_profile_use_case.execute(user_id, update_data)

    mock_user_profile_repository.get_by_id.assert_called_once_with(user_id)
    mock_user_profile_repository.update.assert_called_once()
    mock_unit_of_work.commit.assert_not_called()
    mock_unit_of_work.rollback.assert_called_once()


@pytest.mark.asyncio
async def test_update_user_profile_invalid_id_type(
    update_user_profile_use_case: UpdateUserProfileUseCase, mock_unit_of_work: AsyncMock
):
    """Test updating a user profile with an invalid ID type."""
    with pytest.raises(ValueError, match="user_profile_id must be a valid UUID."):
        await update_user_profile_use_case.execute("not-a-uuid", {"username": "test"})  # type: ignore
    mock_unit_of_work.rollback.assert_not_called()  # Error before UoW begins


@pytest.mark.asyncio
async def test_update_user_profile_empty_update_data(
    update_user_profile_use_case: UpdateUserProfileUseCase, mock_unit_of_work: AsyncMock
):
    """Test updating a user profile with empty update data."""
    user_id = uuid4()
    with pytest.raises(ValueError, match="update_data cannot be empty."):
        await update_user_profile_use_case.execute(user_id, {})
    mock_unit_of_work.rollback.assert_not_called()  # Error before UoW begins


@pytest.mark.asyncio
async def test_update_user_profile_unknown_field_in_update_data(
    update_user_profile_use_case: UpdateUserProfileUseCase,
    mock_user_profile_repository: AsyncMock,
    mock_unit_of_work: AsyncMock,
):
    """Test updating with a field not present in the UserProfile entity."""
    user_id = uuid4()
    existing_profile = UserProfile(id=user_id, username="testuser", email="test@example.com")
    mock_user_profile_repository.get_by_id.return_value = existing_profile
    mock_user_profile_repository.update.return_value = None  # Simulate successful update

    update_data = {"unknown_field": "some_value", "username": "newusername"}

    # The use case logs a warning but proceeds with known fields.
    updated_dto = await update_user_profile_use_case.execute(user_id, update_data)

    mock_user_profile_repository.update.assert_called_once()
    updated_entity_arg = mock_user_profile_repository.update.call_args[0][0]
    assert updated_entity_arg.username == "newusername"
    assert not hasattr(updated_entity_arg, "unknown_field")  # Ensure unknown field was not set

    mock_unit_of_work.commit.assert_called_once()
    assert updated_dto is not None
    assert updated_dto.username == "newusername"


@pytest.mark.asyncio
async def test_update_user_profile_repository_general_exception(
    update_user_profile_use_case: UpdateUserProfileUseCase,
    mock_user_profile_repository: AsyncMock,
    mock_unit_of_work: AsyncMock,
):
    """Test handling of a generic exception from the repository during update."""
    user_id = uuid4()
    existing_profile = UserProfile(id=user_id, username="testuser", email="test@example.com")
    mock_user_profile_repository.get_by_id.return_value = existing_profile
    mock_user_profile_repository.update.side_effect = Exception("Database connection failed")
    update_data = {"username": "newuser"}

    with pytest.raises(
        Exception, match=f"Failed to update user profile {user_id}: Database connection failed"
    ):
        await update_user_profile_use_case.execute(user_id, update_data)

    mock_user_profile_repository.get_by_id.assert_called_once_with(user_id)
    mock_user_profile_repository.update.assert_called_once()
    mock_unit_of_work.commit.assert_not_called()
    mock_unit_of_work.rollback.assert_called_once()


def test_update_user_profile_use_case_invalid_repository_type():
    """Test UpdateUserProfileUseCase init with invalid repository type."""
    with pytest.raises(
        TypeError, match="user_profile_repository must be an instance of IUserProfileRepository"
    ):
        UpdateUserProfileUseCase(MagicMock(), MagicMock(spec=IUnitOfWork))


def test_update_user_profile_use_case_invalid_uow_type():
    """Test UpdateUserProfileUseCase init with invalid unit_of_work type."""
    with pytest.raises(TypeError, match="unit_of_work must be an instance of IUnitOfWork"):
        UpdateUserProfileUseCase(MagicMock(spec=IUserProfileRepository), MagicMock())
