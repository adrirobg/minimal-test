import uuid
from unittest.mock import AsyncMock

import pytest

from src.pkm_app.core.application.use_cases.source.delete_source_use_case import DeleteSourceUseCase
from src.pkm_app.core.domain.errors import (
    PermissionDeniedError,
    RepositoryError,
    SourceNotFoundError,
    ValidationError,
)


@pytest.fixture
def mock_uow_instance():
    mock = AsyncMock()
    mock_uow_entered = AsyncMock()
    mock.sources = mock_uow_entered.sources
    mock.commit = mock_uow_entered.commit
    mock.rollback = mock_uow_entered.rollback
    mock.__aenter__.return_value = mock_uow_entered
    return mock


@pytest.fixture
def delete_source_use_case(mock_uow_instance):
    return DeleteSourceUseCase(unit_of_work=mock_uow_instance)


@pytest.mark.asyncio
async def test_delete_source_success(delete_source_use_case, mock_uow_instance):
    source_id = uuid.uuid4()
    user_id = "test_user_id"

    mock_uow_instance.__aenter__.return_value.sources.delete.return_value = None

    result = await delete_source_use_case.execute(source_id=source_id, user_id=user_id)

    mock_uow_instance.__aenter__.return_value.sources.delete.assert_called_once_with(
        source_id=source_id, user_id=user_id
    )
    mock_uow_instance.__aenter__.return_value.commit.assert_called_once()
    assert result is True


@pytest.mark.asyncio
async def test_delete_source_no_user_id(delete_source_use_case):
    source_id = uuid.uuid4()

    with pytest.raises(PermissionDeniedError) as exc_info:
        await delete_source_use_case.execute(source_id=source_id, user_id="")

    assert "Se requiere ID de usuario para eliminar una fuente." in str(exc_info.value)


@pytest.mark.asyncio
async def test_delete_source_invalid_uuid(delete_source_use_case):
    invalid_source_id = "not-a-uuid"
    user_id = "test_user_id"

    with pytest.raises(ValidationError) as exc_info:
        await delete_source_use_case.execute(source_id=invalid_source_id, user_id=user_id)

    assert "El ID de la fuente debe ser un UUID válido." in str(exc_info.value)


@pytest.mark.asyncio
async def test_delete_source_not_found(delete_source_use_case, mock_uow_instance):
    source_id = uuid.uuid4()
    user_id = "test_user_id"
    error_message = f"Fuente con ID {source_id} no encontrada."

    mock_uow_instance.__aenter__.return_value.sources.delete.side_effect = SourceNotFoundError(
        error_message, source_id=source_id
    )

    with pytest.raises(SourceNotFoundError) as exc_info:
        await delete_source_use_case.execute(source_id=source_id, user_id=user_id)

    error = exc_info.value
    assert str(source_id) in str(error)
    assert error.context.get("operation") == "delete_source"
    assert error.context.get("resource_id") == str(source_id)
    mock_uow_instance.__aenter__.return_value.rollback.assert_called_once()
    mock_uow_instance.__aenter__.return_value.commit.assert_not_called()


@pytest.mark.asyncio
async def test_delete_source_repository_error(delete_source_use_case, mock_uow_instance):
    source_id = uuid.uuid4()
    user_id = "test_user_id"
    mock_uow_instance.__aenter__.return_value.sources.delete.side_effect = Exception(
        "Unexpected DB error"
    )

    with pytest.raises(RepositoryError) as exc_info:
        await delete_source_use_case.execute(source_id=source_id, user_id=user_id)

    assert "Error inesperado en el repositorio al eliminar fuente: Unexpected DB error" in str(
        exc_info.value
    )
    mock_uow_instance.__aenter__.return_value.rollback.assert_called_once()
    mock_uow_instance.__aenter__.return_value.commit.assert_not_called()
