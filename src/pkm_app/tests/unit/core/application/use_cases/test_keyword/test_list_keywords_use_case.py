from datetime import datetime
import uuid
from unittest.mock import AsyncMock, call
import pytest
from typing import List

from src.pkm_app.core.application.dtos import KeywordSchema
from src.pkm_app.core.application.use_cases.keyword.list_keywords_use_case import (
    ListKeywordsUseCase,
)
from src.pkm_app.core.domain.errors import PermissionDeniedError, RepositoryError


@pytest.fixture
def mock_uow_instance():
    mock = AsyncMock()
    mock_keywords_repo = AsyncMock()
    mock.keywords = mock_keywords_repo
    mock.__aenter__.return_value = mock
    return mock


@pytest.fixture
def list_keywords_use_case(mock_uow_instance):
    return ListKeywordsUseCase(unit_of_work=mock_uow_instance)


@pytest.mark.asyncio
async def test_list_keywords_success_default_pagination(
    list_keywords_use_case: ListKeywordsUseCase, mock_uow_instance: AsyncMock
):
    # Arrange
    user_id = "test_user_id"
    expected_keywords = [
        KeywordSchema(
            id=uuid.uuid4(), name="Keyword 1", user_id=user_id, created_at=datetime.now()
        ),
        KeywordSchema(
            id=uuid.uuid4(), name="Keyword 2", user_id=user_id, created_at=datetime.now()
        ),
    ]
    mock_uow_instance.keywords.list_by_user.return_value = expected_keywords

    # Act
    result = await list_keywords_use_case.execute(user_id=user_id)

    # Assert
    mock_uow_instance.keywords.list_by_user.assert_called_once_with(
        user_id=user_id,
        skip=ListKeywordsUseCase.DEFAULT_SKIP,
        limit=ListKeywordsUseCase.DEFAULT_LIMIT,
    )
    assert result == expected_keywords


@pytest.mark.asyncio
async def test_list_keywords_success_custom_pagination(
    list_keywords_use_case: ListKeywordsUseCase, mock_uow_instance: AsyncMock
):
    # Arrange
    user_id = "test_user_id"
    custom_skip = 5
    custom_limit = 10
    expected_keywords = [
        KeywordSchema(
            id=uuid.uuid4(), name="Keyword 1", user_id=user_id, created_at=datetime.now()
        ),
    ]
    mock_uow_instance.keywords.list_by_user.return_value = expected_keywords

    # Act
    result = await list_keywords_use_case.execute(
        user_id=user_id, skip=custom_skip, limit=custom_limit
    )

    # Assert
    mock_uow_instance.keywords.list_by_user.assert_called_once_with(
        user_id=user_id, skip=custom_skip, limit=custom_limit
    )
    assert result == expected_keywords


@pytest.mark.asyncio
async def test_list_keywords_pagination_validation(
    list_keywords_use_case: ListKeywordsUseCase, mock_uow_instance: AsyncMock
):
    # Arrange
    user_id = "test_user_id"
    # Test skip < 0
    await list_keywords_use_case.execute(user_id=user_id, skip=-5, limit=10)
    mock_uow_instance.keywords.list_by_user.assert_called_with(user_id=user_id, skip=0, limit=10)
    mock_uow_instance.keywords.list_by_user.reset_mock()

    # Test limit < 0
    await list_keywords_use_case.execute(user_id=user_id, skip=0, limit=-10)
    mock_uow_instance.keywords.list_by_user.assert_called_with(
        user_id=user_id, skip=0, limit=ListKeywordsUseCase.DEFAULT_LIMIT
    )
    mock_uow_instance.keywords.list_by_user.reset_mock()

    # Test limit > MAX_LIMIT
    await list_keywords_use_case.execute(
        user_id=user_id, skip=0, limit=ListKeywordsUseCase.MAX_LIMIT + 1
    )
    mock_uow_instance.keywords.list_by_user.assert_called_with(
        user_id=user_id, skip=0, limit=ListKeywordsUseCase.MAX_LIMIT
    )


@pytest.mark.asyncio
async def test_list_keywords_empty(
    list_keywords_use_case: ListKeywordsUseCase, mock_uow_instance: AsyncMock
):
    # Arrange
    user_id = "test_user_id"
    mock_uow_instance.keywords.list_by_user.return_value = []  # Simula lista vacía

    # Act
    result = await list_keywords_use_case.execute(user_id=user_id)

    # Assert
    assert result == []
    mock_uow_instance.keywords.list_by_user.assert_called_once_with(
        user_id=user_id,
        skip=ListKeywordsUseCase.DEFAULT_SKIP,
        limit=ListKeywordsUseCase.DEFAULT_LIMIT,
    )


@pytest.mark.asyncio
async def test_list_keywords_no_user_id(list_keywords_use_case: ListKeywordsUseCase):
    # Arrange
    user_id = ""  # Empty user ID

    # Act & Assert
    with pytest.raises(
        PermissionDeniedError, match="Se requiere ID de usuario para listar keywords."
    ):
        await list_keywords_use_case.execute(user_id=user_id)


@pytest.mark.asyncio
async def test_list_keywords_repository_generic_exception(
    list_keywords_use_case: ListKeywordsUseCase, mock_uow_instance: AsyncMock
):
    # Arrange
    user_id = "test_user_id"
    mock_uow_instance.keywords.list_by_user.side_effect = Exception(
        "Simulated generic database error"
    )

    # Act & Assert
    with pytest.raises(
        RepositoryError,
        match="Error inesperado en el repositorio al listar keywords: Simulated generic database error",
    ):
        await list_keywords_use_case.execute(user_id=user_id)
    mock_uow_instance.rollback.assert_called_once()


# Nota: El test_list_keywords_filtered no se implementa directamente aquí
# porque la lógica de filtrado estaría en el repositorio.
# El caso de uso ListKeywordsUseCase actual no toma parámetros de filtrado más allá de la paginación.
# Si se añadiera filtrado al caso de uso, se deberían añadir tests para ello.
