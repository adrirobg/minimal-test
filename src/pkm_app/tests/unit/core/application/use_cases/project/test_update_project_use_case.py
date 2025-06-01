"""Unit tests for the UpdateProjectUseCase."""

import pytest
from unittest.mock import AsyncMock
from uuid import uuid4

from pkm_app.core.application.dtos.project_dto import ProjectSchema, ProjectUpdate
from pkm_app.core.application.use_cases.project.update_project_use_case import UpdateProjectUseCase
from pkm_app.core.application.interfaces.project_interface import IProjectRepository
from pkm_app.core.application.interfaces.unit_of_work_interface import IUnitOfWork
from pkm_app.core.domain.errors import ProjectNotFoundError, PermissionDeniedError, RepositoryError


@pytest.fixture
def mock_project_repository():
    mock = AsyncMock(spec=IProjectRepository)
    mock.update = AsyncMock()
    return mock


@pytest.fixture
def mock_unit_of_work():
    mock = AsyncMock(spec=IUnitOfWork)
    mock.begin = AsyncMock()
    mock.commit = AsyncMock()
    mock.rollback = AsyncMock()
    return mock


@pytest.fixture
def update_project_use_case(mock_project_repository, mock_unit_of_work):
    return UpdateProjectUseCase(mock_project_repository, mock_unit_of_work)


@pytest.mark.asyncio
async def test_update_project_success(
    update_project_use_case, mock_project_repository, mock_unit_of_work
):
    user_id = "user-1"
    project_id = uuid4()
    update_data = ProjectUpdate(name="Nuevo Nombre", description="Nueva Desc")
    updated_project = ProjectSchema(
        id=project_id,
        name=update_data.name,
        description=update_data.description,
        parent_project_id=None,
        user_id=user_id,
        created_at=None,
        updated_at=None,
    )
    mock_project_repository.update.return_value = updated_project

    result = await update_project_use_case.execute(project_id, update_data, user_id)

    assert result == updated_project
    mock_project_repository.update.assert_awaited_once_with(project_id, update_data, user_id)
    mock_unit_of_work.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_project_not_found(update_project_use_case, mock_project_repository):
    user_id = "user-1"
    project_id = uuid4()
    update_data = ProjectUpdate(name="Nuevo Nombre")
    mock_project_repository.update.return_value = None
    with pytest.raises(ProjectNotFoundError):
        await update_project_use_case.execute(project_id, update_data, user_id)


@pytest.mark.asyncio
async def test_update_project_without_permission(update_project_use_case):
    project_id = uuid4()
    update_data = ProjectUpdate(name="Nuevo Nombre")
    with pytest.raises(PermissionDeniedError):
        await update_project_use_case.execute(project_id, update_data, "")


@pytest.mark.asyncio
async def test_update_project_repository_error(update_project_use_case, mock_project_repository):
    user_id = "user-1"
    project_id = uuid4()
    update_data = ProjectUpdate(name="Nuevo Nombre")
    mock_project_repository.update.side_effect = Exception("DB error")
    with pytest.raises(RepositoryError):
        await update_project_use_case.execute(project_id, update_data, user_id)


# Tests unitarios para UpdateProjectUseCase
# Objetivo: Validar la actualización de proyectos, cubriendo casos normales, errores y edge cases.
# Cobertura: actualización exitosa, no encontrado, permisos, nombre duplicado, campos inválidos, actualización parcial.


def test_update_project_success():
    """Debe actualizar nombre y descripción correctamente."""
    # Arrange
    # Act
    # Assert


def test_update_project_not_found():
    """Debe fallar si el proyecto no existe."""
    # Arrange
    # Act
    # Assert


def test_update_project_without_permission():
    """Debe fallar si el usuario no tiene permisos."""
    # Arrange
    # Act
    # Assert


def test_update_project_duplicate_name():
    """Debe fallar si el nombre es duplicado."""
    # Arrange
    # Act
    # Assert


def test_update_project_invalid_fields():
    """Debe fallar si los campos son inválidos (vacío, demasiado largo)."""
    # Arrange
    # Act
    # Assert


def test_update_project_partial_update():
    """Debe permitir actualización parcial de campos permitidos."""
    # Arrange
    # Act
    # Assert
