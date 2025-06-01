"""Unit tests for the CreateUserProfileUseCase."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4, UUID

from pkm_app.core.application.dtos.user_profile_dto import UserProfileDTO
from pkm_app.core.application.use_cases.user_profile.create_user_profile_use_case import (
    CreateUserProfileUseCase,
)
from pkm_app.core.application.interfaces.user_profile_interface import IUserProfileRepository
from pkm_app.core.application.interfaces.unit_of_work_interface import IUnitOfWork
from pkm_app.core.domain.entities.user_profile import UserProfile
from pkm_app.core.domain.errors import DuplicateEntityError


@pytest.fixture
def mock_user_profile_repository():
    """Fixture for a mocked IUserProfileRepository."""
    mock = AsyncMock(spec=IUserProfileRepository)
    # Add all required repository methods
    mock.get_by_email = AsyncMock()
    mock.exists = AsyncMock()
    mock.get_all = AsyncMock()
    mock.add = AsyncMock()
    mock.delete = AsyncMock()
    mock.update = AsyncMock()
    mock.get_by_id = AsyncMock()
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
def create_user_profile_use_case(mock_user_profile_repository, mock_unit_of_work):
    """Fixture for the CreateUserProfileUseCase."""
    return CreateUserProfileUseCase(mock_user_profile_repository, mock_unit_of_work)


@pytest.mark.asyncio
async def test_create_user_profile_valid_data(
    create_user_profile_use_case: CreateUserProfileUseCase,
    mock_user_profile_repository: AsyncMock,
    mock_unit_of_work: AsyncMock,
):
    """Test creating a user profile with valid data."""
    user_id = uuid4()
    user_profile_dto = UserProfileDTO(id=user_id, username="testuser", email="test@example.com")

    # Mock repository methods
    mock_user_profile_repository.get_by_email.return_value = None
    mock_user_profile_repository.add.return_value = None

    created_profile_dto = await create_user_profile_use_case.execute(user_profile_dto)

    mock_user_profile_repository.add.assert_called_once()
    # Check that the argument to add is a UserProfile instance with correct data
    added_profile_arg = mock_user_profile_repository.add.call_args[0][0]
    assert isinstance(added_profile_arg, UserProfile)
    assert added_profile_arg.id == user_id
    assert added_profile_arg.username == "testuser"
    assert added_profile_arg.email == "test@example.com"

    mock_unit_of_work.commit.assert_called_once()
    mock_unit_of_work.rollback.assert_not_called()

    assert created_profile_dto is not None
    assert created_profile_dto.id == user_id
    assert created_profile_dto.username == "testuser"
    assert created_profile_dto.email == "test@example.com"


# Eliminado: test_create_user_profile_generates_id_if_not_provided
# El DTO requiere 'id' como obligatorio, por lo que este test ya no es válido.


@pytest.mark.asyncio
async def test_create_user_profile_duplicate_email(
    create_user_profile_use_case: CreateUserProfileUseCase,
    mock_user_profile_repository: AsyncMock,
    mock_unit_of_work: AsyncMock,
):
    """Test creating a user profile when email already exists."""
    user_profile_dto = UserProfileDTO(
        id=uuid4(), username="testuser", email="duplicate@example.com"
    )

    # Simulate repository raising an error for duplicate entry
    # In a real scenario, this might be a more specific DB error like IntegrityError
    mock_user_profile_repository.add.side_effect = DuplicateEntityError("Email already exists.")

    with pytest.raises(Exception, match="Failed to create user profile: Email already exists."):
        await create_user_profile_use_case.execute(user_profile_dto)

    mock_user_profile_repository.add.assert_called_once()
    mock_unit_of_work.commit.assert_not_called()
    assert mock_unit_of_work.rollback.call_count >= 1


@pytest.mark.asyncio
async def test_create_user_profile_invalid_data_type(
    create_user_profile_use_case: CreateUserProfileUseCase, mock_unit_of_work: AsyncMock
):
    """Test creating a user profile with invalid data type for DTO."""
    with pytest.raises(ValueError, match="user_profile_data must be a UserProfileDTO instance."):
        await create_user_profile_use_case.execute(None)  # type: ignore

    mock_unit_of_work.commit.assert_not_called()
    mock_unit_of_work.rollback.assert_not_called()  # Rollback not called if error before UoW begins


@pytest.mark.asyncio
async def test_create_user_profile_repository_general_exception(
    create_user_profile_use_case: CreateUserProfileUseCase,
    mock_user_profile_repository: AsyncMock,
    mock_unit_of_work: AsyncMock,
):
    """Test handling of a generic exception from the repository."""
    user_profile_dto = UserProfileDTO(id=uuid4(), username="testuser", email="test@example.com")
    mock_user_profile_repository.add.side_effect = Exception("Database connection error")

    with pytest.raises(Exception, match="Failed to create user profile: Database connection error"):
        await create_user_profile_use_case.execute(user_profile_dto)

    mock_user_profile_repository.add.assert_called_once()
    mock_unit_of_work.commit.assert_not_called()
    assert mock_unit_of_work.rollback.call_count >= 1


def test_create_user_profile_use_case_invalid_repository_type():
    """Test CreateUserProfileUseCase init with invalid repository type."""
    with pytest.raises(
        TypeError, match="user_profile_repository must be an instance of IUserProfileRepository"
    ):
        CreateUserProfileUseCase(MagicMock(), MagicMock(spec=IUnitOfWork))


def test_create_user_profile_use_case_invalid_uow_type():
    """Test CreateUserProfileUseCase init with invalid unit_of_work type."""
    with pytest.raises(TypeError, match="unit_of_work must be an instance of IUnitOfWork"):
        CreateUserProfileUseCase(MagicMock(spec=IUserProfileRepository), MagicMock())
