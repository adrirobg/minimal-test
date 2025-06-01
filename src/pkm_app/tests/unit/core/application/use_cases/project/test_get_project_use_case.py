"""Unit tests for the GetProjectUseCase."""

import pytest
from unittest.mock import AsyncMock
from uuid import uuid4

from pkm_app.core.application.dtos.project_dto import ProjectSchema
from pkm_app.core.application.use_cases.project.get_project_use_case import GetProjectUseCase
from pkm_app.core.application.interfaces.project_interface import IProjectRepository
from pkm_app.core.application.interfaces.unit_of_work_interface import IUnitOfWork
from pkm_app.core.domain.errors import ProjectNotFoundError, PermissionDeniedError, RepositoryError


@pytest.fixture
def mock_project_repository():
    mock = AsyncMock(spec=IProjectRepository)
    mock.get_by_id = AsyncMock()
    return mock


@pytest.fixture
def mock_unit_of_work():
    mock = AsyncMock(spec=IUnitOfWork)
    mock.begin = AsyncMock()
    mock.commit = AsyncMock()
    mock.rollback = AsyncMock()
    return mock


@pytest.fixture
def get_project_use_case(mock_project_repository, mock_unit_of_work):
    return GetProjectUseCase(mock_project_repository, mock_unit_of_work)


@pytest.mark.asyncio
async def test_get_project_success(
    get_project_use_case, mock_project_repository, mock_unit_of_work
):
    user_id = "user-1"
    project_id = uuid4()
    project_schema = ProjectSchema(
        id=project_id,
        name="Proyecto Test",
        description="Desc",
        parent_project_id=None,
        user_id=user_id,
        created_at=None,
        updated_at=None,
    )
    mock_project_repository.get_by_id.return_value = project_schema

    result = await get_project_use_case.execute(project_id, user_id)

    assert result == project_schema
    mock_project_repository.get_by_id.assert_awaited_once_with(project_id, user_id)
    mock_unit_of_work.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_project_not_found(get_project_use_case, mock_project_repository):
    user_id = "user-1"
    project_id = uuid4()
    mock_project_repository.get_by_id.return_value = None
    with pytest.raises(ProjectNotFoundError):
        await get_project_use_case.execute(project_id, user_id)


@pytest.mark.asyncio
async def test_get_project_without_permission(get_project_use_case):
    project_id = uuid4()
    with pytest.raises(PermissionDeniedError):
        await get_project_use_case.execute(project_id, "")


@pytest.mark.asyncio
async def test_get_project_invalid_id(get_project_use_case):
    user_id = "user-1"
    with pytest.raises(ProjectNotFoundError):
        await get_project_use_case.execute(None, user_id)


@pytest.mark.asyncio
async def test_get_project_repository_error(get_project_use_case, mock_project_repository):
    user_id = "user-1"
    project_id = uuid4()
    mock_project_repository.get_by_id.side_effect = Exception("DB error")
    with pytest.raises(RepositoryError):
        await get_project_use_case.execute(project_id, user_id)


# Tests unitarios para GetProjectUseCase
# Objetivo: Validar la obtención de proyectos por ID, cubriendo casos normales, errores y edge cases.
# Cobertura: proyecto existente, no encontrado, permisos, todos los campos, ID inválido.


def test_get_project_success():
    """Debe obtener un proyecto existente por ID."""
    # Arrange
    # Act
    # Assert


def test_get_project_not_found():
    """Debe fallar si el proyecto no existe."""
    # Arrange
    # Act
    # Assert


def test_get_project_without_permission():
    """Debe fallar si el usuario no tiene permisos."""
    # Arrange
    # Act
    # Assert


def test_get_project_all_fields():
    """Debe obtener proyecto con todos los campos completos."""
    # Arrange
    # Act
    # Assert


def test_get_project_invalid_id():
    """Debe fallar con ID inválido (None, string, negativo)."""
    # Arrange
    # Act
    # Assert
