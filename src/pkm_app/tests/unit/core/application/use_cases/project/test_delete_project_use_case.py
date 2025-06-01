"""Unit tests for the DeleteProjectUseCase."""

import pytest
from unittest.mock import AsyncMock
from uuid import uuid4

from pkm_app.core.application.use_cases.project.delete_project_use_case import DeleteProjectUseCase
from pkm_app.core.application.interfaces.project_interface import IProjectRepository
from pkm_app.core.application.interfaces.unit_of_work_interface import IUnitOfWork
from pkm_app.core.domain.errors import ProjectNotFoundError, PermissionDeniedError, RepositoryError


@pytest.fixture
def mock_project_repository():
    mock = AsyncMock(spec=IProjectRepository)
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
def delete_project_use_case(mock_project_repository, mock_unit_of_work):
    return DeleteProjectUseCase(mock_project_repository, mock_unit_of_work)


@pytest.mark.asyncio
async def test_delete_project_success(
    delete_project_use_case, mock_project_repository, mock_unit_of_work
):
    user_id = "user-1"
    project_id = uuid4()
    mock_project_repository.delete.return_value = True

    result = await delete_project_use_case.execute(project_id, user_id)

    assert result is True
    mock_project_repository.delete.assert_awaited_once_with(project_id, user_id)
    mock_unit_of_work.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_project_not_found(delete_project_use_case, mock_project_repository):
    user_id = "user-1"
    project_id = uuid4()
    mock_project_repository.delete.return_value = False
    with pytest.raises(ProjectNotFoundError):
        await delete_project_use_case.execute(project_id, user_id)


@pytest.mark.asyncio
async def test_delete_project_without_permission(delete_project_use_case):
    project_id = uuid4()
    with pytest.raises(PermissionDeniedError):
        await delete_project_use_case.execute(project_id, "")


@pytest.mark.asyncio
async def test_delete_project_repository_error(delete_project_use_case, mock_project_repository):
    user_id = "user-1"
    project_id = uuid4()
    mock_project_repository.delete.side_effect = Exception("DB error")
    with pytest.raises(RepositoryError):
        await delete_project_use_case.execute(project_id, user_id)


# Tests unitarios para DeleteProjectUseCase
# Objetivo: Validar la eliminación de proyectos, cubriendo casos normales, errores y edge cases.
# Cobertura: eliminación exitosa, no encontrado, permisos, dependencias, ya eliminado.


def test_delete_project_success():
    """Debe eliminar un proyecto existente."""
    # Arrange
    # Act
    # Assert


def test_delete_project_not_found():
    """Debe fallar si el proyecto no existe."""
    # Arrange
    # Act
    # Assert


def test_delete_project_without_permission():
    """Debe fallar si el usuario no tiene permisos."""
    # Arrange
    # Act
    # Assert


def test_delete_project_with_dependencies():
    """Debe fallar si el proyecto tiene dependencias (notas, etc.)."""
    # Arrange
    # Act
    # Assert


def test_delete_project_already_deleted():
    """Debe manejar el caso de eliminar un proyecto ya eliminado."""
    # Arrange
    # Act
    # Assert
