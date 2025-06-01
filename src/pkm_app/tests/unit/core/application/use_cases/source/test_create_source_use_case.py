import uuid
from unittest.mock import AsyncMock
from datetime import datetime, timezone

import pytest
from pydantic import AnyUrl

from src.pkm_app.core.application.dtos import SourceCreate, SourceSchema
from src.pkm_app.core.application.use_cases.source.create_source_use_case import CreateSourceUseCase
from src.pkm_app.core.domain.errors import PermissionDeniedError, ValidationError, RepositoryError


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
def create_source_use_case(mock_uow_instance):
    return CreateSourceUseCase(unit_of_work=mock_uow_instance)


@pytest.mark.asyncio
async def test_create_source_success(create_source_use_case, mock_uow_instance):
    source_create_data = SourceCreate(
        title="Test Source", type="article", description="Test Description", url="https://test.com"
    )
    user_id = "test_user_id"
    expected_source_id = uuid.uuid4()

    mock_uow_instance.__aenter__.return_value.sources.create.return_value = SourceSchema(
        id=expected_source_id,
        user_id=user_id,
        title="Test Source",
        type="article",
        description="Test Description",
        url=AnyUrl("https://test.com"),
        link_metadata={},
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    result = await create_source_use_case.execute(source_in=source_create_data, user_id=user_id)

    mock_uow_instance.__aenter__.return_value.sources.create.assert_called_once_with(
        source_in=source_create_data, user_id=user_id
    )
    mock_uow_instance.__aenter__.return_value.commit.assert_called_once()
    assert isinstance(result, SourceSchema)
    assert result.title == "Test Source"
    assert result.type == "article"
    assert result.description == "Test Description"
    assert str(result.url) == "https://test.com/"
    assert result.user_id == user_id
    assert result.id == expected_source_id


@pytest.mark.asyncio
async def test_create_source_no_user_id(create_source_use_case):
    source_create_data = SourceCreate(title="Test Source")
    with pytest.raises(PermissionDeniedError) as exc_info:
        await create_source_use_case.execute(source_in=source_create_data, user_id="")
    assert "Se requiere ID de usuario para crear una fuente." in str(exc_info.value)


@pytest.mark.asyncio
async def test_create_source_no_title(create_source_use_case):
    source_create_data = SourceCreate(title="")
    user_id = "test_user_id"
    with pytest.raises(ValidationError) as exc_info:
        await create_source_use_case.execute(source_in=source_create_data, user_id=user_id)
    assert "El título de la fuente no puede estar vacío." in str(exc_info.value)


@pytest.mark.asyncio
async def test_create_source_invalid_url(create_source_use_case, mock_uow_instance):
    source_create_data = SourceCreate(title="Test Source", url="https://test.com")
    user_id = "test_user_id"
    mock_uow_instance.__aenter__.return_value.sources.create.side_effect = ValueError(
        "URL inválida"
    )

    with pytest.raises(ValidationError) as exc_info:
        await create_source_use_case.execute(source_in=source_create_data, user_id=user_id)

    assert "URL inválida" in str(exc_info.value)
    mock_uow_instance.__aenter__.return_value.rollback.assert_called_once()
    mock_uow_instance.__aenter__.return_value.commit.assert_not_called()


@pytest.mark.asyncio
async def test_create_source_repository_error(create_source_use_case, mock_uow_instance):
    source_create_data = SourceCreate(title="Test Source")
    user_id = "test_user_id"
    mock_uow_instance.__aenter__.return_value.sources.create.side_effect = ValueError(
        "Error de validación en el repositorio"
    )

    with pytest.raises(ValidationError) as exc_info:
        await create_source_use_case.execute(source_in=source_create_data, user_id=user_id)

    assert "Error de validación en el repositorio" in str(exc_info.value)
    mock_uow_instance.__aenter__.return_value.rollback.assert_called_once()
    mock_uow_instance.__aenter__.return_value.commit.assert_not_called()


@pytest.mark.asyncio
async def test_create_source_generic_exception(create_source_use_case, mock_uow_instance):
    source_create_data = SourceCreate(title="Test Source")
    user_id = "test_user_id"
    mock_uow_instance.__aenter__.return_value.sources.create.side_effect = Exception(
        "Unexpected DB error"
    )

    with pytest.raises(RepositoryError) as exc_info:
        await create_source_use_case.execute(source_in=source_create_data, user_id=user_id)

    assert "Error inesperado en el repositorio al crear fuente: Unexpected DB error" in str(
        exc_info.value
    )
    mock_uow_instance.__aenter__.return_value.rollback.assert_called_once()
    mock_uow_instance.__aenter__.return_value.commit.assert_not_called()
