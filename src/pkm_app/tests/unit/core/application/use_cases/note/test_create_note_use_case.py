import uuid
from unittest.mock import AsyncMock
from datetime import datetime, timezone

import pytest

from src.pkm_app.core.application.dtos import NoteCreate, NoteSchema
from src.pkm_app.core.application.use_cases.note.create_note_use_case import (
    CreateNoteUseCase,
)
from src.pkm_app.core.domain.errors import PermissionDeniedError, ValidationError, RepositoryError


@pytest.fixture
def mock_uow_instance():  # Renamed to avoid confusion if mock_uow itself is used elsewhere
    mock = AsyncMock()
    # Mock the __aenter__ and __aexit__ methods for async context management
    # The __aenter__ method should return the mock itself, or a specific part of it
    # if the UoW instance used inside the `async with` block is different.
    # Here, we assume the `uow` passed to the use case IS the context manager.
    # So, its `notes` attribute should be the one configured.
    # If `self.unit_of_work` is a factory, then `mock_uow.return_value.__aenter__.return_value.notes...`
    # For now, assume `mock_uow` is the UoW instance.
    mock_uow_entered = AsyncMock()
    mock.notes = mock_uow_entered.notes  # Alias for easier access in tests
    mock.projects = mock_uow_entered.projects  # Alias
    mock.commit = mock_uow_entered.commit
    mock.rollback = mock_uow_entered.rollback
    mock.__aenter__.return_value = (
        mock_uow_entered  # This is what `uow` will be inside the `async with`
    )
    return mock


@pytest.fixture
def create_note_use_case(mock_uow_instance):  # Use the correctly configured mock
    return CreateNoteUseCase(unit_of_work=mock_uow_instance)


@pytest.mark.asyncio
async def test_create_note_success(create_note_use_case, mock_uow_instance):
    note_create_data = NoteCreate(content="Test content", title="Test Note")
    user_id = "test_user_id"
    expected_note_id = uuid.uuid4()
    # Configure the mock that is returned by __aenter__
    mock_uow_instance.__aenter__.return_value.notes.create.return_value = NoteSchema(
        id=expected_note_id,
        user_id=user_id,
        content="Test content",
        title="Test Note",
        keywords=[],
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    result = await create_note_use_case.execute(note_in=note_create_data, user_id=user_id)

    mock_uow_instance.__aenter__.return_value.notes.create.assert_called_once_with(
        note_in=note_create_data, user_id=user_id
    )
    mock_uow_instance.__aenter__.return_value.commit.assert_called_once()
    assert isinstance(result, NoteSchema)
    assert result.content == "Test content"
    assert result.title == "Test Note"
    assert result.user_id == user_id
    assert result.id == expected_note_id


@pytest.mark.asyncio
async def test_create_note_no_user_id(create_note_use_case):
    note_create_data = NoteCreate(content="Test content")
    with pytest.raises(PermissionDeniedError) as exc_info:
        await create_note_use_case.execute(note_in=note_create_data, user_id="")
    assert "Se requiere ID de usuario para crear una nota." in str(exc_info.value)


@pytest.mark.asyncio
async def test_create_note_no_content(create_note_use_case):
    note_create_data = NoteCreate(content="")  # Contenido vacío
    user_id = "test_user_id"
    with pytest.raises(ValidationError) as exc_info:
        await create_note_use_case.execute(note_in=note_create_data, user_id=user_id)
    assert "El contenido de la nota no puede estar vacío." in str(exc_info.value)


@pytest.mark.asyncio
async def test_create_note_repository_validation_error(create_note_use_case, mock_uow_instance):
    note_create_data = NoteCreate(content="Test content", project_id=uuid.uuid4())
    user_id = "test_user_id"
    # Configure the mock that is returned by __aenter__
    mock_uow_instance.__aenter__.return_value.notes.create.side_effect = ValueError(
        "Proyecto no encontrado"
    )

    with pytest.raises(ValidationError) as exc_info:
        await create_note_use_case.execute(note_in=note_create_data, user_id=user_id)

    assert "Proyecto no encontrado" in str(exc_info.value)
    mock_uow_instance.__aenter__.return_value.rollback.assert_called_once()
    mock_uow_instance.__aenter__.return_value.commit.assert_not_called()


@pytest.mark.asyncio
async def test_create_note_generic_exception(create_note_use_case, mock_uow_instance):
    note_create_data = NoteCreate(content="Test content")
    user_id = "test_user_id"
    # Configure the mock that is returned by __aenter__
    mock_uow_instance.__aenter__.return_value.notes.create.side_effect = Exception(
        "Unexpected DB error"
    )

    with pytest.raises(RepositoryError) as exc_info:  # Adjusted to expect RepositoryError
        await create_note_use_case.execute(note_in=note_create_data, user_id=user_id)

    assert "Error inesperado en el repositorio al crear nota: Unexpected DB error" in str(
        exc_info.value
    )
    mock_uow_instance.__aenter__.return_value.rollback.assert_called_once()
    mock_uow_instance.__aenter__.return_value.commit.assert_not_called()
