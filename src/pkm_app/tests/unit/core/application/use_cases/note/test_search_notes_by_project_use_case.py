import uuid
from unittest.mock import AsyncMock
from datetime import datetime, timezone

import pytest

from src.pkm_app.core.application.dtos import NoteSchema, ProjectSchema
from src.pkm_app.core.application.use_cases.note.search_notes_by_project_use_case import (
    SearchNotesByProjectUseCase,
)
from src.pkm_app.core.domain.errors import (
    PermissionDeniedError,
    ProjectNotFoundError,
    ValidationError,
    RepositoryError,
)


@pytest.fixture
def mock_uow_instance():
    mock = AsyncMock()
    mock_uow_entered = AsyncMock()
    mock.notes = mock_uow_entered.notes
    mock.projects = mock_uow_entered.projects
    mock.commit = mock_uow_entered.commit
    mock.rollback = mock_uow_entered.rollback
    mock.__aenter__.return_value = mock_uow_entered
    return mock


@pytest.fixture
def search_notes_by_project_use_case(mock_uow_instance):
    return SearchNotesByProjectUseCase(unit_of_work=mock_uow_instance)


@pytest.mark.asyncio
async def test_search_notes_by_project_success(search_notes_by_project_use_case, mock_uow_instance):
    project_id = uuid.uuid4()
    user_id = "test_user_id"
    skip = 0
    limit = 10
    now = datetime.now(timezone.utc)
    mock_project = ProjectSchema(
        id=project_id, user_id=user_id, name="Test Project", created_at=now, updated_at=now
    )
    expected_notes = [
        NoteSchema(
            id=uuid.uuid4(),
            user_id=user_id,
            content="Note 1 for project",
            project_id=project_id,
            keywords=[],
            created_at=now,
            updated_at=now,
        ),
        NoteSchema(
            id=uuid.uuid4(),
            user_id=user_id,
            content="Note 2 for project",
            project_id=project_id,
            keywords=[],
            created_at=now,
            updated_at=now,
        ),
    ]
    mock_uow_instance.__aenter__.return_value.projects.get_by_id.return_value = mock_project
    mock_uow_instance.__aenter__.return_value.notes.search_by_project.return_value = expected_notes

    result_project, result_notes = await search_notes_by_project_use_case.execute(
        project_id=project_id, user_id=user_id, skip=skip, limit=limit
    )

    mock_uow_instance.__aenter__.return_value.projects.get_by_id.assert_called_once_with(
        project_id=project_id, user_id=user_id
    )
    mock_uow_instance.__aenter__.return_value.notes.search_by_project.assert_called_once_with(
        project_id=project_id, user_id=user_id, skip=skip, limit=limit
    )
    assert result_project == mock_project
    assert result_notes == expected_notes


@pytest.mark.asyncio
async def test_search_notes_project_not_found(search_notes_by_project_use_case, mock_uow_instance):
    project_id = uuid.uuid4()
    user_id = "test_user_id"
    mock_uow_instance.__aenter__.return_value.projects.get_by_id.return_value = (
        None  # Proyecto no encontrado
    )

    with pytest.raises(ProjectNotFoundError) as exc_info:
        await search_notes_by_project_use_case.execute(project_id=project_id, user_id=user_id)

    assert f"Proyecto con ID {project_id} no encontrado o no pertenece al usuario." in str(
        exc_info.value
    )
    mock_uow_instance.__aenter__.return_value.projects.get_by_id.assert_called_once_with(
        project_id=project_id, user_id=user_id
    )
    mock_uow_instance.__aenter__.return_value.notes.search_by_project.assert_not_called()
    mock_uow_instance.__aenter__.return_value.rollback.assert_called_once()


@pytest.mark.asyncio
async def test_search_notes_no_user_id(search_notes_by_project_use_case):
    project_id = uuid.uuid4()
    with pytest.raises(PermissionDeniedError) as exc_info:
        await search_notes_by_project_use_case.execute(project_id=project_id, user_id="")
    assert "Se requiere ID de usuario para buscar notas por proyecto." in str(exc_info.value)


@pytest.mark.asyncio
async def test_search_notes_no_project_id(search_notes_by_project_use_case):
    user_id = "test_user_id"
    with pytest.raises(ValidationError) as exc_info:
        await search_notes_by_project_use_case.execute(project_id=None, user_id=user_id)  # type: ignore
    assert "Se requiere ID de proyecto para la búsqueda." in str(exc_info.value)


@pytest.mark.asyncio
async def test_search_notes_empty_result(search_notes_by_project_use_case, mock_uow_instance):
    project_id = uuid.uuid4()
    user_id = "test_user_id"
    now = datetime.now(timezone.utc)
    mock_project = ProjectSchema(
        id=project_id, user_id=user_id, name="Test Project", created_at=now, updated_at=now
    )
    mock_uow_instance.__aenter__.return_value.projects.get_by_id.return_value = mock_project
    mock_uow_instance.__aenter__.return_value.notes.search_by_project.return_value = (
        []
    )  # No hay notas

    # Usa los valores por defecto para skip y limit del caso de uso
    expected_skip = SearchNotesByProjectUseCase.DEFAULT_SKIP
    expected_limit = SearchNotesByProjectUseCase.DEFAULT_LIMIT

    result_project, result_notes = await search_notes_by_project_use_case.execute(
        project_id=project_id, user_id=user_id
    )

    assert result_project == mock_project
    assert result_notes == []
    mock_uow_instance.__aenter__.return_value.notes.search_by_project.assert_called_once_with(
        project_id=project_id, user_id=user_id, skip=expected_skip, limit=expected_limit
    )


@pytest.mark.asyncio
async def test_search_notes_by_project_pagination_validation(
    search_notes_by_project_use_case, mock_uow_instance
):
    project_id = uuid.uuid4()
    user_id = "test_user_id"
    now = datetime.now(timezone.utc)
    mock_project = ProjectSchema(
        id=project_id, user_id=user_id, name="Test Project", created_at=now, updated_at=now
    )
    mock_uow_instance.__aenter__.return_value.projects.get_by_id.return_value = mock_project
    mock_uow_instance.__aenter__.return_value.notes.search_by_project.return_value = []

    # Test con skip y limit inválidos
    await search_notes_by_project_use_case.execute(
        project_id=project_id,
        user_id=user_id,
        skip=-5,
        limit=SearchNotesByProjectUseCase.MAX_LIMIT + 10,
    )
    mock_uow_instance.__aenter__.return_value.notes.search_by_project.assert_called_with(
        project_id=project_id,
        user_id=user_id,
        skip=SearchNotesByProjectUseCase.DEFAULT_SKIP,  # Corregido a DEFAULT_SKIP
        limit=SearchNotesByProjectUseCase.MAX_LIMIT,  # Corregido a MAX_LIMIT
    )


@pytest.mark.asyncio
async def test_search_notes_by_project_repository_error_on_get_project(
    search_notes_by_project_use_case, mock_uow_instance
):
    project_id = uuid.uuid4()
    user_id = "test_user_id"
    mock_uow_instance.__aenter__.return_value.projects.get_by_id.side_effect = Exception(
        "DB error getting project"
    )

    with pytest.raises(RepositoryError) as exc_info:
        await search_notes_by_project_use_case.execute(project_id=project_id, user_id=user_id)
    assert (
        "Error inesperado en el repositorio al buscar notas por proyecto: DB error getting project"
        in str(exc_info.value)
    )
    mock_uow_instance.__aenter__.return_value.rollback.assert_called_once()


@pytest.mark.asyncio
async def test_search_notes_by_project_repository_error_on_search_notes(
    search_notes_by_project_use_case, mock_uow_instance
):
    project_id = uuid.uuid4()
    user_id = "test_user_id"
    now = datetime.now(timezone.utc)
    mock_project = ProjectSchema(
        id=project_id, user_id=user_id, name="Test Project", created_at=now, updated_at=now
    )
    mock_uow_instance.__aenter__.return_value.projects.get_by_id.return_value = mock_project
    mock_uow_instance.__aenter__.return_value.notes.search_by_project.side_effect = Exception(
        "DB error searching notes"
    )

    with pytest.raises(RepositoryError) as exc_info:
        await search_notes_by_project_use_case.execute(project_id=project_id, user_id=user_id)
    assert (
        "Error inesperado en el repositorio al buscar notas por proyecto: DB error searching notes"
        in str(exc_info.value)
    )
    mock_uow_instance.__aenter__.return_value.rollback.assert_called_once()
