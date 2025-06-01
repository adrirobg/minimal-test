"""Unit tests for the DeleteUserProfileUseCase."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4, UUID

from pkm_app.core.application.use_cases.user_profile.delete_user_profile_use_case import (
    DeleteUserProfileUseCase,
)
from pkm_app.core.application.interfaces.user_profile_interface import IUserProfileRepository
from pkm_app.core.application.interfaces.unit_of_work_interface import IUnitOfWork
from pkm_app.core.domain.entities.user_profile import UserProfile  # For mock return
from pkm_app.core.domain.errors import EntityNotFoundError


@pytest.fixture
def mock_user_profile_repository():
    """Fixture for a mocked IUserProfileRepository."""
    mock = AsyncMock(spec=IUserProfileRepository)
    # Add all required repository methods
    mock.exists = AsyncMock()
    mock.get_by_id = AsyncMock()
    mock.get_by_email = AsyncMock()
    mock.get_all = AsyncMock()
    mock.add = AsyncMock()
    mock.delete = AsyncMock()
    mock.update = AsyncMock()
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
def delete_user_profile_use_case(mock_user_profile_repository, mock_unit_of_work):
    """Fixture for the DeleteUserProfileUseCase."""
    return DeleteUserProfileUseCase(mock_user_profile_repository, mock_unit_of_work)


@pytest.mark.asyncio
async def test_delete_user_profile_existing_id(
    delete_user_profile_use_case: DeleteUserProfileUseCase,
    mock_user_profile_repository: AsyncMock,
    mock_unit_of_work: AsyncMock,
):
    """Test deleting an existing user profile."""
    user_id = uuid4()
    # Mock repository methods
    mock_user_profile_repository.exists.return_value = True
    mock_user_profile_repository.delete.return_value = True  # Simulate successful deletion

    result = await delete_user_profile_use_case.execute(user_id)

    mock_user_profile_repository.exists.assert_called_once_with(user_id)
    mock_user_profile_repository.delete.assert_called_once_with(user_id)
    mock_unit_of_work.commit.assert_called_once()
    mock_unit_of_work.rollback.assert_not_called()
    assert result is True


@pytest.mark.asyncio
async def test_delete_user_profile_non_existing_id(
    delete_user_profile_use_case: DeleteUserProfileUseCase,
    mock_user_profile_repository: AsyncMock,
    mock_unit_of_work: AsyncMock,
):
    """Test deleting a user profile with a non-existing ID."""
    non_existing_id = uuid4()
    mock_user_profile_repository.exists.return_value = False  # Simulate profile not found

    with pytest.raises(
        EntityNotFoundError, match=f"User profile with ID '{non_existing_id}' not found."
    ):
        await delete_user_profile_use_case.execute(non_existing_id)

    mock_user_profile_repository.exists.assert_called_once_with(non_existing_id)
    mock_user_profile_repository.delete.assert_not_called()
    mock_unit_of_work.commit.assert_not_called()
    assert mock_unit_of_work.rollback.call_count >= 1


@pytest.mark.asyncio
async def test_delete_user_profile_invalid_id_type(
    delete_user_profile_use_case: DeleteUserProfileUseCase, mock_unit_of_work: AsyncMock
):
    """Test deleting a user profile with an invalid ID type."""
    with pytest.raises(ValueError, match="user_profile_id must be a valid UUID."):
        await delete_user_profile_use_case.execute("not-a-uuid")  # type: ignore

    # No se exige rollback porque el error ocurre antes de iniciar la transacción


@pytest.mark.asyncio
async def test_delete_user_profile_repository_exists_exception(
    delete_user_profile_use_case: DeleteUserProfileUseCase,
    mock_user_profile_repository: AsyncMock,
    mock_unit_of_work: AsyncMock,
):
    """Test handling of a generic exception from repository's exists()."""
    user_id = uuid4()
    mock_user_profile_repository.exists.side_effect = Exception(
        "Database connection error during exists"
    )

    with pytest.raises(
        Exception,
        match=f"Failed to delete user profile {user_id}: Database connection error during exists",
    ):
        await delete_user_profile_use_case.execute(user_id)

    mock_user_profile_repository.exists.assert_called_once_with(user_id)
    mock_user_profile_repository.delete.assert_not_called()
    mock_unit_of_work.commit.assert_not_called()
    assert mock_unit_of_work.rollback.call_count >= 1


@pytest.mark.asyncio
async def test_delete_user_profile_repository_delete_exception(
    delete_user_profile_use_case: DeleteUserProfileUseCase,
    mock_user_profile_repository: AsyncMock,
    mock_unit_of_work: AsyncMock,
):
    """Test handling of a generic exception from repository's delete."""
    user_id = uuid4()
    mock_user_profile_repository.exists.return_value = True
    mock_user_profile_repository.delete.side_effect = Exception(
        "Database connection error during delete"
    )

    with pytest.raises(
        Exception,
        match=f"Failed to delete user profile {user_id}: Database connection error during delete",
    ):
        await delete_user_profile_use_case.execute(user_id)

    mock_user_profile_repository.exists.assert_called_once_with(user_id)
    mock_user_profile_repository.delete.assert_called_once_with(user_id)
    mock_unit_of_work.commit.assert_not_called()
    assert mock_unit_of_work.rollback.call_count >= 1


def test_delete_user_profile_use_case_invalid_repository_type():
    """Test DeleteUserProfileUseCase init with invalid repository type."""
    with pytest.raises(
        TypeError, match="user_profile_repository must be an instance of IUserProfileRepository"
    ):
        DeleteUserProfileUseCase(MagicMock(), MagicMock(spec=IUnitOfWork))


def test_delete_user_profile_use_case_invalid_uow_type():
    """Test DeleteUserProfileUseCase init with invalid unit_of_work type."""
    with pytest.raises(TypeError, match="unit_of_work must be an instance of IUnitOfWork"):
        DeleteUserProfileUseCase(MagicMock(spec=IUserProfileRepository), MagicMock())


# Note on "Elimina perfil con relaciones (edge case)":
# This specific scenario (handling relations like cascade delete or restriction)
# is typically managed at the database schema level or within the repository's
# delete implementation (e.g., by catching ForeignKeyViolation errors).
# The use case itself, as designed, would either succeed if the repository/DB handles it,
# or fail if a restriction is violated and the repository raises an error.
# Testing this aspect thoroughly would often require integration tests with a real DB
# or more complex mocking of repository behavior based on such constraints.
# The current unit test (test_delete_user_profile_existing_id) implicitly covers
# the "happy path" where deletion (including any cascade) is successful.
# A specific test for "restriction" would involve mocking `delete` to raise an
# appropriate error (e.g., IntegrityError or a custom domain error).
