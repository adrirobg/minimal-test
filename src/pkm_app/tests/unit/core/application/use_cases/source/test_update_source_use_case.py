import uuid
from unittest.mock import AsyncMock
from datetime import datetime, timezone

import pytest
from pydantic import AnyUrl

from src.pkm_app.core.application.dtos import SourceSchema, SourceUpdate
from src.pkm_app.core.application.use_cases.source.update_source_use_case import UpdateSourceUseCase
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
def update_source_use_case(mock_uow_instance):
    return UpdateSourceUseCase(unit_of_work=mock_uow_instance)


@pytest.mark.asyncio
async def test_update_source_success(update_source_use_case, mock_uow_instance):
    source_id = uuid.uuid4()
    user_id = "test_user_id"
    source_update = SourceUpdate(
        title="Updated Source",
        type="book",
        description="Updated Description",
        url="https://updated-test.com",
    )

    updated_source = SourceSchema(
        id=source_id,
        user_id=user_id,
        title="Updated Source",
        type="book",
        description="Updated Description",
        url=AnyUrl("https://updated-test.com"),
        link_metadata={},
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    mock_uow_instance.__aenter__.return_value.sources.update.return_value = updated_source

    result = await update_source_use_case.execute(
        source_id=source_id, source_in=source_update, user_id=user_id
    )

    mock_uow_instance.__aenter__.return_value.sources.update.assert_called_once_with(
        source_id=source_id, source_in=source_update, user_id=user_id
    )
    mock_uow_instance.__aenter__.return_value.commit.assert_called_once()
    assert isinstance(result, SourceSchema)
    assert result.id == source_id
    assert result.title == "Updated Source"
    assert result.type == "book"
    assert result.description == "Updated Description"
    assert str(result.url) == "https://updated-test.com/"


@pytest.mark.asyncio
async def test_update_source_not_found(update_source_use_case, mock_uow_instance):
    source_id = uuid.uuid4()
    user_id = "test_user_id"
    source_update = SourceUpdate(title="Updated Source")

    mock_uow_instance.__aenter__.return_value.sources.update.side_effect = SourceNotFoundError(
        f"Fuente no encontrada: {source_id}", source_id=source_id
    )

    with pytest.raises(SourceNotFoundError) as exc_info:
        await update_source_use_case.execute(
            source_id=source_id, source_in=source_update, user_id=user_id
        )

    error = exc_info.value
    assert str(source_id) in str(error)
    assert error.context.get("operation") == "update_source"
    assert error.context.get("resource_id") == str(source_id)
    mock_uow_instance.__aenter__.return_value.rollback.assert_called_once()
    mock_uow_instance.__aenter__.return_value.commit.assert_not_called()


@pytest.mark.asyncio
async def test_update_source_no_user_id(update_source_use_case):
    source_id = uuid.uuid4()
    source_update = SourceUpdate(title="Updated Source")

    with pytest.raises(PermissionDeniedError) as exc_info:
        await update_source_use_case.execute(
            source_id=source_id, source_in=source_update, user_id=""
        )

    assert "Se requiere ID de usuario para actualizar una fuente." in str(exc_info.value)


@pytest.mark.asyncio
async def test_update_source_invalid_uuid(update_source_use_case):
    invalid_source_id = "not-a-uuid"
    user_id = "test_user_id"
    source_update = SourceUpdate(title="Updated Source")

    with pytest.raises(ValidationError) as exc_info:
        await update_source_use_case.execute(
            source_id=invalid_source_id, source_in=source_update, user_id=user_id
        )

    assert "El ID de la fuente debe ser un UUID válido." in str(exc_info.value)


@pytest.mark.asyncio
async def test_update_source_empty_update(update_source_use_case):
    source_id = uuid.uuid4()
    user_id = "test_user_id"
    source_update = SourceUpdate()

    with pytest.raises(ValidationError) as exc_info:
        await update_source_use_case.execute(
            source_id=source_id, source_in=source_update, user_id=user_id
        )

    assert "No se proporcionaron datos para actualizar la fuente." in str(exc_info.value)


@pytest.mark.asyncio
async def test_update_source_empty_title(update_source_use_case):
    source_id = uuid.uuid4()
    user_id = "test_user_id"
    source_update = SourceUpdate(title="")

    with pytest.raises(ValidationError) as exc_info:
        await update_source_use_case.execute(
            source_id=source_id, source_in=source_update, user_id=user_id
        )

    assert "El título de la fuente no puede ser vacío si se actualiza." in str(exc_info.value)


@pytest.mark.asyncio
async def test_update_source_invalid_url(update_source_use_case, mock_uow_instance):
    source_id = uuid.uuid4()
    user_id = "test_user_id"
    source_update = SourceUpdate(title="Test Source", url="https://test.com")

    mock_uow_instance.__aenter__.return_value.sources.update.side_effect = ValueError(
        "URL inválida"
    )

    with pytest.raises(ValidationError) as exc_info:
        await update_source_use_case.execute(
            source_id=source_id, source_in=source_update, user_id=user_id
        )

    assert "URL inválida" in str(exc_info.value)
    mock_uow_instance.__aenter__.return_value.rollback.assert_called_once()
    mock_uow_instance.__aenter__.return_value.commit.assert_not_called()


@pytest.mark.asyncio
async def test_update_source_repository_error(update_source_use_case, mock_uow_instance):
    source_id = uuid.uuid4()
    user_id = "test_user_id"
    source_update = SourceUpdate(title="Updated Source")

    mock_uow_instance.__aenter__.return_value.sources.update.side_effect = Exception(
        "Unexpected DB error"
    )

    with pytest.raises(RepositoryError) as exc_info:
        await update_source_use_case.execute(
            source_id=source_id, source_in=source_update, user_id=user_id
        )

    assert "Error inesperado en el repositorio al actualizar fuente: Unexpected DB error" in str(
        exc_info.value
    )
    mock_uow_instance.__aenter__.return_value.rollback.assert_called_once()
    mock_uow_instance.__aenter__.return_value.commit.assert_not_called()


@pytest.mark.asyncio
async def test_update_source_validation_error(update_source_use_case, mock_uow_instance):
    source_id = uuid.uuid4()
    user_id = "test_user_id"
    source_update = SourceUpdate(title="Updated Source")

    mock_uow_instance.__aenter__.return_value.sources.update.side_effect = ValueError(
        "Error de validación en el repositorio"
    )

    with pytest.raises(ValidationError) as exc_info:
        await update_source_use_case.execute(
            source_id=source_id, source_in=source_update, user_id=user_id
        )

    assert "Error de validación en el repositorio" in str(exc_info.value)
    mock_uow_instance.__aenter__.return_value.rollback.assert_called_once()
    mock_uow_instance.__aenter__.return_value.commit.assert_not_called()
