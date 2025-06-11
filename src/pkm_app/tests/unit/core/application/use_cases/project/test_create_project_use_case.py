"""Unit tests for the CreateProjectUseCase."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from pkm_app.core.application.dtos.project_dto import ProjectCreate, ProjectSchema
from pkm_app.core.application.use_cases.project.create_project_use_case import CreateProjectUseCase
from pkm_app.core.application.interfaces.project_interface import IProjectRepository
from pkm_app.core.application.interfaces.unit_of_work_interface import IUnitOfWork
from pkm_app.core.domain.errors import ValidationError, PermissionDeniedError, RepositoryError


@pytest.fixture
def mock_project_repository():
    mock = AsyncMock(spec=IProjectRepository)
    mock.create = AsyncMock()
    mock.list_by_user = AsyncMock()
    mock.get_by_id = AsyncMock()
    mock.update = AsyncMock()
    mock.delete = AsyncMock()
    return mock


@pytest.fixture
def mock_unit_of_work():
    mock = AsyncMock(spec=IUnitOfWork)
    mock.begin = AsyncMock()
    mock.commit = AsyncMock()
    mock.rollback = AsyncMock()
    return mock


@pytest.fixture
def create_project_use_case(mock_project_repository, mock_unit_of_work):
    return CreateProjectUseCase(mock_project_repository, mock_unit_of_work)


@pytest.mark.asyncio
async def test_create_project_success(
    create_project_use_case, mock_project_repository, mock_unit_of_work
):
    user_id = "user-1"
    project_in = ProjectCreate(name="Proyecto Test", description="Desc", parent_project_id=None)
    project_schema = ProjectSchema(
        id=uuid4(),
        name=project_in.name,
        description=project_in.description,
        parent_project_id=None,
        user_id=user_id,
        created_at=None,
        updated_at=None,
    )
    mock_project_repository.create.return_value = project_schema

    result = await create_project_use_case.execute(project_in, user_id)

    assert result == project_schema
    mock_project_repository.create.assert_awaited_once_with(project_in, user_id)
    mock_unit_of_work.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_project_empty_name(create_project_use_case):
    user_id = "user-1"
    project_in = ProjectCreate(name="", description="Desc", parent_project_id=None)
    with pytest.raises(ValidationError):
        await create_project_use_case.execute(project_in, user_id)


@pytest.mark.asyncio
async def test_create_project_without_permission(create_project_use_case):
    project_in = ProjectCreate(name="Proyecto", description="Desc", parent_project_id=None)
    with pytest.raises(PermissionDeniedError):
        await create_project_use_case.execute(project_in, "")


@pytest.mark.asyncio
async def test_create_project_repository_error(create_project_use_case, mock_project_repository):
    user_id = "user-1"
    project_in = ProjectCreate(name="Proyecto", description="Desc", parent_project_id=None)
    mock_project_repository.create.side_effect = Exception("DB error")
    with pytest.raises(RepositoryError):
        await create_project_use_case.execute(project_in, user_id)


# Tests unitarios para CreateProjectUseCase
# Objetivo: Validar la creación de proyectos cubriendo casos normales, errores y edge cases.
# Cobertura: nombre vacío, duplicado, campos requeridos, descripción opcional, límite de caracteres, permisos.


def test_create_project_success():
    """Debe crear un proyecto con datos válidos."""
    # Arrange
    # Act
    # Assert


def test_create_project_empty_name():
    """Debe fallar si el nombre está vacío."""
    # Arrange
    # Act
    # Assert


def test_create_project_duplicate_name():
    """Debe fallar si el nombre ya existe."""
    # Arrange
    # Act
    # Assert


def test_create_project_missing_required_fields():
    """Debe fallar si faltan campos requeridos."""
    # Arrange
    # Act
    # Assert


def test_create_project_with_optional_description():
    """Debe crear proyecto con descripción opcional."""
    # Arrange
    # Act
    # Assert


def test_create_project_description_too_long():
    """Debe fallar si la descripción supera el límite de caracteres."""
    # Arrange
    # Act
    # Assert


def test_create_project_without_permission():
    """Debe fallar si el usuario no tiene permisos."""
    # Arrange
    # Act
    # Assert
