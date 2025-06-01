import uuid
from unittest.mock import AsyncMock
from datetime import datetime, timezone

import pytest

from src.pkm_app.core.application.dtos import NoteSchema
from src.pkm_app.core.application.use_cases.note.list_notes_use_case import (
    ListNotesUseCase,
)
from src.pkm_app.core.domain.errors import PermissionDeniedError, RepositoryError


@pytest.fixture
def mock_uow_instance():
    mock = AsyncMock()
    mock_uow_entered = AsyncMock()
    mock.notes = mock_uow_entered.notes
    mock.commit = mock_uow_entered.commit  # No se usa en list, pero por completitud
    mock.rollback = mock_uow_entered.rollback  # No se usa en list, pero por completitud
    mock.__aenter__.return_value = mock_uow_entered
    return mock


@pytest.fixture
def list_notes_use_case(mock_uow_instance):
    return ListNotesUseCase(unit_of_work=mock_uow_instance)


@pytest.mark.asyncio
async def test_list_notes_success(list_notes_use_case, mock_uow_instance):
    user_id = "test_user_id"
    skip = 5
    limit = 10
    now = datetime.now(timezone.utc)
    expected_notes = [
        NoteSchema(
            id=uuid.uuid4(),
            user_id=user_id,
            content="Test content 1",
            title="Test Note 1",
            keywords=[],
            created_at=now,
            updated_at=now,
        ),
        NoteSchema(
            id=uuid.uuid4(),
            user_id=user_id,
            content="Test content 2",
            title="Test Note 2",
            keywords=[],
            created_at=now,
            updated_at=now,
        ),
    ]
    mock_uow_instance.__aenter__.return_value.notes.list_by_user.return_value = expected_notes

    result = await list_notes_use_case.execute(user_id=user_id, skip=skip, limit=limit)

    mock_uow_instance.__aenter__.return_value.notes.list_by_user.assert_called_once_with(
        user_id=user_id, skip=skip, limit=limit
    )
    assert result == expected_notes


@pytest.mark.asyncio
async def test_list_notes_default_pagination(list_notes_use_case, mock_uow_instance):
    user_id = "test_user_id"
    expected_notes = []
    mock_uow_instance.__aenter__.return_value.notes.list_by_user.return_value = expected_notes

    await list_notes_use_case.execute(user_id=user_id)  # Uses default skip/limit

    mock_uow_instance.__aenter__.return_value.notes.list_by_user.assert_called_once_with(
        user_id=user_id, skip=ListNotesUseCase.DEFAULT_SKIP, limit=ListNotesUseCase.DEFAULT_LIMIT
    )


@pytest.mark.asyncio
async def test_list_notes_custom_pagination(list_notes_use_case, mock_uow_instance):
    user_id = "test_user_id"
    skip = 10
    limit = 20
    expected_notes = []
    mock_uow_instance.__aenter__.return_value.notes.list_by_user.return_value = expected_notes

    await list_notes_use_case.execute(user_id=user_id, skip=skip, limit=limit)

    mock_uow_instance.__aenter__.return_value.notes.list_by_user.assert_called_once_with(
        user_id=user_id, skip=skip, limit=limit
    )


@pytest.mark.asyncio
async def test_list_notes_pagination_validation_negative_skip(
    list_notes_use_case, mock_uow_instance
):
    user_id = "test_user_id"
    mock_uow_instance.__aenter__.return_value.notes.list_by_user.return_value = []
    await list_notes_use_case.execute(user_id=user_id, skip=-5, limit=10)
    mock_uow_instance.__aenter__.return_value.notes.list_by_user.assert_called_once_with(
        user_id=user_id, skip=ListNotesUseCase.DEFAULT_SKIP, limit=10
    )


@pytest.mark.asyncio
async def test_list_notes_pagination_validation_negative_limit(
    list_notes_use_case, mock_uow_instance
):
    user_id = "test_user_id"
    mock_uow_instance.__aenter__.return_value.notes.list_by_user.return_value = []
    await list_notes_use_case.execute(user_id=user_id, skip=0, limit=-10)
    mock_uow_instance.__aenter__.return_value.notes.list_by_user.assert_called_once_with(
        user_id=user_id, skip=0, limit=ListNotesUseCase.DEFAULT_LIMIT
    )


@pytest.mark.asyncio
async def test_list_notes_pagination_validation_exceed_max_limit(
    list_notes_use_case, mock_uow_instance
):
    user_id = "test_user_id"
    mock_uow_instance.__aenter__.return_value.notes.list_by_user.return_value = []
    await list_notes_use_case.execute(user_id=user_id, skip=0, limit=ListNotesUseCase.MAX_LIMIT + 1)
    mock_uow_instance.__aenter__.return_value.notes.list_by_user.assert_called_once_with(
        user_id=user_id, skip=0, limit=ListNotesUseCase.MAX_LIMIT
    )


@pytest.mark.asyncio
async def test_list_notes_no_user_id(list_notes_use_case):
    with pytest.raises(PermissionDeniedError) as exc_info:
        await list_notes_use_case.execute(user_id="")
    assert "Se requiere ID de usuario para listar notas." in str(exc_info.value)


@pytest.mark.asyncio
async def test_list_notes_empty_result(list_notes_use_case, mock_uow_instance):
    user_id = "test_user_id"
    mock_uow_instance.__aenter__.return_value.notes.list_by_user.return_value = []

    result = await list_notes_use_case.execute(user_id=user_id)  # Uses default skip/limit

    assert result == []
    mock_uow_instance.__aenter__.return_value.notes.list_by_user.assert_called_once_with(
        user_id=user_id, skip=ListNotesUseCase.DEFAULT_SKIP, limit=ListNotesUseCase.DEFAULT_LIMIT
    )


@pytest.mark.asyncio
async def test_list_notes_repository_exception(list_notes_use_case, mock_uow_instance):
    user_id = "test_user_id"
    mock_uow_instance.__aenter__.return_value.notes.list_by_user.side_effect = Exception("DB error")

    with pytest.raises(RepositoryError) as exc_info:
        await list_notes_use_case.execute(user_id=user_id)

    assert "Error inesperado en el repositorio al listar notas: DB error" in str(exc_info.value)
    mock_uow_instance.__aenter__.return_value.rollback.assert_called_once()
