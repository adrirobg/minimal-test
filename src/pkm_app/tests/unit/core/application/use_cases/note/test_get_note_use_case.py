import uuid
from unittest.mock import AsyncMock
from datetime import datetime, timezone

import pytest

from src.pkm_app.core.application.dtos import NoteSchema
from src.pkm_app.core.application.use_cases.note.get_note_use_case import (
    GetNoteUseCase,
)
from src.pkm_app.core.domain.errors import NoteNotFoundError, PermissionDeniedError


@pytest.fixture
def mock_uow_instance():
    mock = AsyncMock()
    mock_uow_entered = AsyncMock()
    mock.notes = mock_uow_entered.notes
    # No necesitamos commit/rollback para get, pero los mockeamos por si acaso
    mock.commit = mock_uow_entered.commit
    mock.rollback = mock_uow_entered.rollback
    mock.__aenter__.return_value = mock_uow_entered
    return mock


@pytest.fixture
def get_note_use_case(mock_uow_instance):
    return GetNoteUseCase(unit_of_work=mock_uow_instance)


@pytest.mark.asyncio
async def test_get_note_success(get_note_use_case, mock_uow_instance):
    note_id = uuid.uuid4()
    user_id = "test_user_id"
    now = datetime.now(timezone.utc)
    expected_note = NoteSchema(
        id=note_id,
        user_id=user_id,
        content="Test content",
        title="Test Note",
        keywords=[],
        created_at=now,
        updated_at=now,
    )
    mock_uow_instance.__aenter__.return_value.notes.get_by_id.return_value = expected_note

    result = await get_note_use_case.execute(note_id=note_id, user_id=user_id)

    mock_uow_instance.__aenter__.return_value.notes.get_by_id.assert_called_once_with(
        note_id=note_id, user_id=user_id
    )
    assert result == expected_note


@pytest.mark.asyncio
async def test_get_note_not_found(get_note_use_case, mock_uow_instance):
    note_id = uuid.uuid4()
    user_id = "test_user_id"
    mock_uow_instance.__aenter__.return_value.notes.get_by_id.return_value = None

    with pytest.raises(NoteNotFoundError) as exc_info:
        await get_note_use_case.execute(note_id=note_id, user_id=user_id)

    assert f"Nota con ID {note_id} no encontrada o no pertenece al usuario." in str(exc_info.value)
    mock_uow_instance.__aenter__.return_value.notes.get_by_id.assert_called_once_with(
        note_id=note_id, user_id=user_id
    )
    # Rollback se llama incluso en lectura si hay excepción, según el patrón
    mock_uow_instance.__aenter__.return_value.rollback.assert_called_once()


@pytest.mark.asyncio
async def test_get_note_no_user_id(get_note_use_case):
    note_id = uuid.uuid4()
    with pytest.raises(PermissionDeniedError) as exc_info:
        await get_note_use_case.execute(note_id=note_id, user_id="")
    assert "Se requiere ID de usuario para obtener una nota." in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_note_no_note_id(get_note_use_case):
    user_id = "test_user_id"
    with pytest.raises(NoteNotFoundError) as exc_info:
        await get_note_use_case.execute(note_id=None, user_id=user_id)  # type: ignore
    assert "Se requiere ID de nota para obtenerla." in str(exc_info.value)
