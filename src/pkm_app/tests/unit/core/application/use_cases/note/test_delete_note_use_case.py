import uuid
from unittest.mock import AsyncMock

import pytest

from src.pkm_app.core.application.use_cases.note.delete_note_use_case import (
    DeleteNoteUseCase,
)
from src.pkm_app.core.domain.errors import (
    NoteNotFoundError,
    PermissionDeniedError,
    RepositoryError,
)


@pytest.fixture
def mock_uow_instance():
    mock = AsyncMock()
    mock_uow_entered = AsyncMock()
    mock.notes = mock_uow_entered.notes
    mock.commit = mock_uow_entered.commit
    mock.rollback = mock_uow_entered.rollback
    mock.__aenter__.return_value = mock_uow_entered
    return mock


@pytest.fixture
def delete_note_use_case(mock_uow_instance):
    return DeleteNoteUseCase(unit_of_work=mock_uow_instance)


@pytest.mark.asyncio
async def test_delete_note_success(delete_note_use_case, mock_uow_instance):
    note_id = uuid.uuid4()
    user_id = "test_user_id"
    # El método delete del repo no devuelve nada si tiene éxito, o lanza excepción
    mock_uow_instance.__aenter__.return_value.notes.delete.return_value = None

    result = await delete_note_use_case.execute(note_id=note_id, user_id=user_id)

    mock_uow_instance.__aenter__.return_value.notes.delete.assert_called_once_with(
        note_id=note_id, user_id=user_id
    )
    mock_uow_instance.__aenter__.return_value.commit.assert_called_once()
    assert result is True


@pytest.mark.asyncio
async def test_delete_note_not_found(delete_note_use_case, mock_uow_instance):
    note_id = uuid.uuid4()
    user_id = "test_user_id"
    # Configurar el mock para que lance NoteNotFoundError
    error_message = f"Nota con ID {note_id} no encontrada para eliminar."
    mock_uow_instance.__aenter__.return_value.notes.delete.side_effect = NoteNotFoundError(
        error_message, note_id=note_id
    )

    with pytest.raises(NoteNotFoundError) as exc_info:
        await delete_note_use_case.execute(note_id=note_id, user_id=user_id)

    assert error_message in str(exc_info.value)
    mock_uow_instance.__aenter__.return_value.notes.delete.assert_called_once_with(
        note_id=note_id, user_id=user_id
    )
    mock_uow_instance.__aenter__.return_value.rollback.assert_called_once()
    mock_uow_instance.__aenter__.return_value.commit.assert_not_called()


@pytest.mark.asyncio
async def test_delete_note_no_user_id(delete_note_use_case):
    note_id = uuid.uuid4()
    with pytest.raises(PermissionDeniedError) as exc_info:
        await delete_note_use_case.execute(note_id=note_id, user_id="")
    assert "Se requiere ID de usuario para eliminar una nota." in str(exc_info.value)


@pytest.mark.asyncio
async def test_delete_note_no_note_id(delete_note_use_case):
    user_id = "test_user_id"
    with pytest.raises(NoteNotFoundError) as exc_info:
        await delete_note_use_case.execute(note_id=None, user_id=user_id)  # type: ignore
    assert "Se requiere ID de nota para eliminarla." in str(exc_info.value)


@pytest.mark.asyncio
async def test_delete_note_repository_exception(delete_note_use_case, mock_uow_instance):
    note_id = uuid.uuid4()
    user_id = "test_user_id"
    mock_uow_instance.__aenter__.return_value.notes.delete.side_effect = Exception(
        "DB error on delete"
    )

    with pytest.raises(RepositoryError) as exc_info:  # Espera RepositoryError
        await delete_note_use_case.execute(note_id=note_id, user_id=user_id)

    assert "Error inesperado en el repositorio al eliminar nota: DB error on delete" in str(
        exc_info.value
    )
    mock_uow_instance.__aenter__.return_value.rollback.assert_called_once()
    mock_uow_instance.__aenter__.return_value.commit.assert_not_called()
