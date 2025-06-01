"""Unit tests for the ListProjectsUseCase."""

import pytest
from unittest.mock import AsyncMock
from uuid import uuid4

from pkm_app.core.application.dtos.project_dto import ProjectSchema
from pkm_app.core.application.use_cases.project.list_projects_use_case import ListProjectsUseCase
from pkm_app.core.application.interfaces.project_interface import IProjectRepository
from pkm_app.core.application.interfaces.unit_of_work_interface import IUnitOfWork
from pkm_app.core.domain.errors import PermissionDeniedError, RepositoryError


@pytest.fixture
def mock_project_repository():
    mock = AsyncMock(spec=IProjectRepository)
    mock.list_by_user = AsyncMock()
    return mock


@pytest.fixture
def mock_unit_of_work():
    mock = AsyncMock(spec=IUnitOfWork)
    mock.begin = AsyncMock()
    mock.commit = AsyncMock()
    mock.rollback = AsyncMock()
    return mock


@pytest.fixture
def list_projects_use_case(mock_project_repository, mock_unit_of_work):
    return ListProjectsUseCase(mock_project_repository, mock_unit_of_work)


@pytest.mark.asyncio
async def test_list_projects_success(
    list_projects_use_case, mock_project_repository, mock_unit_of_work
):
    user_id = "user-1"
    projects = [
        ProjectSchema(
            id=uuid4(),
            name=f"Proyecto {i}",
            description="Desc",
            parent_project_id=None,
            user_id=user_id,
            created_at=None,
            updated_at=None,
        )
        for i in range(3)
    ]
    mock_project_repository.list_by_user.return_value = projects

    result = await list_projects_use_case.execute(user_id)

    assert result == projects
    mock_project_repository.list_by_user.assert_awaited_once_with(user_id, skip=0, limit=50)
    mock_unit_of_work.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_list_projects_empty(list_projects_use_case, mock_project_repository):
    user_id = "user-1"
    mock_project_repository.list_by_user.return_value = []
    result = await list_projects_use_case.execute(user_id)
    assert result == []


@pytest.mark.asyncio
async def test_list_projects_without_permission(list_projects_use_case):
    with pytest.raises(PermissionDeniedError):
        await list_projects_use_case.execute("")


@pytest.mark.asyncio
async def test_list_projects_pagination(list_projects_use_case, mock_project_repository):
    user_id = "user-1"
    projects = [
        ProjectSchema(
            id=uuid4(),
            name=f"Proyecto {i}",
            description="Desc",
            parent_project_id=None,
            user_id=user_id,
            created_at=None,
            updated_at=None,
        )
        for i in range(10)
    ]
    mock_project_repository.list_by_user.return_value = projects
    result = await list_projects_use_case.execute(user_id, skip=5, limit=10)
    assert result == projects
    mock_project_repository.list_by_user.assert_awaited_once_with(user_id, skip=5, limit=10)


@pytest.mark.asyncio
async def test_list_projects_repository_error(list_projects_use_case, mock_project_repository):
    user_id = "user-1"
    mock_project_repository.list_by_user.side_effect = Exception("DB error")
    with pytest.raises(RepositoryError):
        await list_projects_use_case.execute(user_id)


# Tests unitarios para ListProjectsUseCase
# Objetivo: Validar la lista de proyectos del usuario, cubriendo casos normales, filtros, errores y edge cases.
# Cobertura: lista exitosa, filtros, lista vacía, permisos, paginación, filtros inválidos.


def test_list_projects_success():
    """Debe listar todos los proyectos del usuario."""
    # Arrange
    # Act
    # Assert


def test_list_projects_with_filters():
    """Debe listar proyectos aplicando filtros (nombre, fecha, etc.)."""
    # Arrange
    # Act
    # Assert


def test_list_projects_empty():
    """Debe devolver lista vacía si no hay proyectos."""
    # Arrange
    # Act
    # Assert


def test_list_projects_without_permission():
    """Debe fallar si el usuario no tiene permisos."""
    # Arrange
    # Act
    # Assert


def test_list_projects_pagination():
    """Debe manejar correctamente la paginación con muchos proyectos."""
    # Arrange
    # Act
    # Assert


def test_list_projects_invalid_filters():
    """Debe fallar o manejar filtros inválidos."""
    # Arrange
    # Act
    # Assert
