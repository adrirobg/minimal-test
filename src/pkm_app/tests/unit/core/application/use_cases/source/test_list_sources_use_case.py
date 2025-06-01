import uuid
from unittest.mock import AsyncMock
from datetime import datetime, timezone

import pytest
from pydantic import AnyUrl

from src.pkm_app.core.application.dtos import SourceSchema
from src.pkm_app.core.application.use_cases.source.list_sources_use_case import ListSourcesUseCase
from src.pkm_app.core.domain.errors import PermissionDeniedError, RepositoryError


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
def list_sources_use_case(mock_uow_instance):
    return ListSourcesUseCase(unit_of_work=mock_uow_instance)


@pytest.fixture
def sample_sources():
    user_id = "test_user_id"
    return [
        SourceSchema(
            id=uuid.uuid4(),
            user_id=user_id,
            title=f"Test Source {i}",
            type="article",
            description=f"Description {i}",
            url=AnyUrl(f"https://test{i}.com"),
            link_metadata={},
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        for i in range(3)
    ]


@pytest.mark.asyncio
async def test_list_sources_success(list_sources_use_case, mock_uow_instance, sample_sources):
    user_id = "test_user_id"
    mock_uow_instance.__aenter__.return_value.sources.list_by_user.return_value = sample_sources

    result = await list_sources_use_case.execute(user_id=user_id)

    mock_uow_instance.__aenter__.return_value.sources.list_by_user.assert_called_once_with(
        user_id=user_id, skip=0, limit=50
    )
    assert len(result) == 3
    assert all(isinstance(source, SourceSchema) for source in result)
    assert all(source.user_id == user_id for source in result)


@pytest.mark.asyncio
async def test_list_sources_empty(list_sources_use_case, mock_uow_instance):
    user_id = "test_user_id"
    mock_uow_instance.__aenter__.return_value.sources.list_by_user.return_value = []

    result = await list_sources_use_case.execute(user_id=user_id)

    assert isinstance(result, list)
    assert len(result) == 0
    mock_uow_instance.__aenter__.return_value.sources.list_by_user.assert_called_once_with(
        user_id=user_id, skip=0, limit=50
    )


@pytest.mark.asyncio
async def test_list_sources_with_pagination(
    list_sources_use_case, mock_uow_instance, sample_sources
):
    user_id = "test_user_id"
    skip = 1
    limit = 2
    mock_uow_instance.__aenter__.return_value.sources.list_by_user.return_value = sample_sources[
        1:3
    ]

    result = await list_sources_use_case.execute(user_id=user_id, skip=skip, limit=limit)

    mock_uow_instance.__aenter__.return_value.sources.list_by_user.assert_called_once_with(
        user_id=user_id, skip=skip, limit=limit
    )
    assert len(result) == 2


@pytest.mark.asyncio
async def test_list_sources_no_user_id(list_sources_use_case):
    with pytest.raises(PermissionDeniedError) as exc_info:
        await list_sources_use_case.execute(user_id="")
    assert "Se requiere ID de usuario para listar fuentes." in str(exc_info.value)


@pytest.mark.asyncio
async def test_list_sources_negative_skip(list_sources_use_case, mock_uow_instance, sample_sources):
    user_id = "test_user_id"
    mock_uow_instance.__aenter__.return_value.sources.list_by_user.return_value = sample_sources

    result = await list_sources_use_case.execute(user_id=user_id, skip=-1)

    mock_uow_instance.__aenter__.return_value.sources.list_by_user.assert_called_once_with(
        user_id=user_id, skip=0, limit=50
    )
    assert len(result) == 3


@pytest.mark.asyncio
async def test_list_sources_negative_limit(
    list_sources_use_case, mock_uow_instance, sample_sources
):
    user_id = "test_user_id"
    mock_uow_instance.__aenter__.return_value.sources.list_by_user.return_value = sample_sources

    result = await list_sources_use_case.execute(user_id=user_id, limit=-1)

    mock_uow_instance.__aenter__.return_value.sources.list_by_user.assert_called_once_with(
        user_id=user_id, skip=0, limit=50
    )
    assert len(result) == 3


@pytest.mark.asyncio
async def test_list_sources_exceed_max_limit(
    list_sources_use_case, mock_uow_instance, sample_sources
):
    user_id = "test_user_id"
    mock_uow_instance.__aenter__.return_value.sources.list_by_user.return_value = sample_sources

    result = await list_sources_use_case.execute(user_id=user_id, limit=150)

    mock_uow_instance.__aenter__.return_value.sources.list_by_user.assert_called_once_with(
        user_id=user_id, skip=0, limit=100
    )
    assert len(result) == 3


@pytest.mark.asyncio
async def test_list_sources_repository_error(list_sources_use_case, mock_uow_instance):
    user_id = "test_user_id"
    mock_uow_instance.__aenter__.return_value.sources.list_by_user.side_effect = Exception(
        "Unexpected DB error"
    )

    with pytest.raises(RepositoryError) as exc_info:
        await list_sources_use_case.execute(user_id=user_id)

    assert "Error inesperado en el repositorio al listar fuentes: Unexpected DB error" in str(
        exc_info.value
    )
    mock_uow_instance.__aenter__.return_value.rollback.assert_called_once()
