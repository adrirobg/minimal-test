import uuid
from unittest.mock import AsyncMock
from datetime import datetime, timezone

import pytest
from pydantic import AnyUrl

from src.pkm_app.core.application.dtos import SourceSchema
from src.pkm_app.core.application.use_cases.source.get_source_use_case import GetSourceUseCase
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
def get_source_use_case(mock_uow_instance):
    return GetSourceUseCase(unit_of_work=mock_uow_instance)


@pytest.mark.asyncio
async def test_get_source_success(get_source_use_case, mock_uow_instance):
    source_id = uuid.uuid4()
    user_id = "test_user_id"
    expected_source = SourceSchema(
        id=source_id,
        user_id=user_id,
        title="Test Source",
        type="article",
        description="Test Description",
        url=AnyUrl("https://test.com"),
        link_metadata={},
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    mock_uow_instance.__aenter__.return_value.sources.get_by_id.return_value = expected_source

    result = await get_source_use_case.execute(source_id=source_id, user_id=user_id)

    mock_uow_instance.__aenter__.return_value.sources.get_by_id.assert_called_once_with(
        source_id=source_id, user_id=user_id
    )
    assert isinstance(result, SourceSchema)
    assert result.id == source_id
    assert result.user_id == user_id
    assert result.title == "Test Source"
    assert result.type == "article"
    assert result.description == "Test Description"
    assert str(result.url) == "https://test.com/"


@pytest.mark.asyncio
async def test_get_source_no_user_id(get_source_use_case):
    source_id = uuid.uuid4()
    with pytest.raises(PermissionDeniedError) as exc_info:
        await get_source_use_case.execute(source_id=source_id, user_id="")
    assert "Se requiere ID de usuario para obtener una fuente." in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_source_not_found(get_source_use_case, mock_uow_instance):
    source_id = uuid.uuid4()
    user_id = "test_user_id"
    mock_uow_instance.__aenter__.return_value.sources.get_by_id.return_value = None

    with pytest.raises(SourceNotFoundError) as exc_info:
        await get_source_use_case.execute(source_id=source_id, user_id=user_id)

    assert f"Fuente con ID {source_id} no encontrada o no pertenece al usuario." in str(
        exc_info.value
    )
    mock_uow_instance.__aenter__.return_value.rollback.assert_called_once()


@pytest.mark.asyncio
async def test_get_source_invalid_uuid(get_source_use_case):
    invalid_source_id = "not-a-uuid"
    user_id = "test_user_id"

    with pytest.raises(ValidationError) as exc_info:
        await get_source_use_case.execute(source_id=invalid_source_id, user_id=user_id)

    assert "El ID de la fuente debe ser un UUID válido." in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_source_repository_error(get_source_use_case, mock_uow_instance):
    source_id = uuid.uuid4()
    user_id = "test_user_id"
    mock_uow_instance.__aenter__.return_value.sources.get_by_id.side_effect = Exception(
        "Unexpected DB error"
    )

    with pytest.raises(RepositoryError) as exc_info:
        await get_source_use_case.execute(source_id=source_id, user_id=user_id)

    assert "Error inesperado en el repositorio al obtener fuente: Unexpected DB error" in str(
        exc_info.value
    )
    mock_uow_instance.__aenter__.return_value.rollback.assert_called_once()


@pytest.mark.asyncio
async def test_get_source_not_found_error_propagation(get_source_use_case, mock_uow_instance):
    source_id = uuid.uuid4()
    user_id = "test_user_id"
    mock_uow_instance.__aenter__.return_value.sources.get_by_id.side_effect = SourceNotFoundError(
        f"Fuente con ID {source_id} no encontrada.",
        source_id=source_id,
        context={"custom": "context"},
    )

    with pytest.raises(SourceNotFoundError) as exc_info:
        await get_source_use_case.execute(source_id=source_id, user_id=user_id)

    assert "Fuente con ID" in str(exc_info.value)
    assert exc_info.value.context.get("operation") == "get_source"
    assert exc_info.value.context.get("custom") == "context"
    mock_uow_instance.__aenter__.return_value.rollback.assert_called_once()
