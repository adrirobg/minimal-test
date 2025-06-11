import uuid
from unittest.mock import AsyncMock
import pytest

from src.pkm_app.core.application.dtos import KeywordSchema
from src.pkm_app.core.application.use_cases.keyword.get_keyword_use_case import GetKeywordUseCase
from src.pkm_app.core.domain.errors import (
    EntityNotFoundError,
    PermissionDeniedError,
    ValidationError,
    RepositoryError,
)


@pytest.fixture
def mock_uow_instance():  # Se puede reutilizar el fixture si es general
    mock = AsyncMock()
    mock_keywords_repo = AsyncMock()
    mock.keywords = mock_keywords_repo
    mock.__aenter__.return_value = mock
    return mock


@pytest.fixture
def get_keyword_use_case(mock_uow_instance):
    return GetKeywordUseCase(unit_of_work=mock_uow_instance)


@pytest.mark.asyncio
async def test_get_keyword_success(
    get_keyword_use_case: GetKeywordUseCase, mock_uow_instance: AsyncMock
):
    # Arrange
    keyword_id = uuid.uuid4()
    user_id = "test_user_id"
    from datetime import datetime

    expected_keyword = KeywordSchema(
        id=keyword_id, name="Test Keyword", user_id=user_id, created_at=datetime.now()
    )
    mock_uow_instance.keywords.get_by_id.return_value = expected_keyword

    # Act
    result = await get_keyword_use_case.execute(keyword_id=keyword_id, user_id=user_id)

    # Assert
    mock_uow_instance.keywords.get_by_id.assert_called_once_with(
        entity_id=keyword_id, user_id=user_id
    )
    assert result == expected_keyword


@pytest.mark.asyncio
async def test_get_keyword_not_found(
    get_keyword_use_case: GetKeywordUseCase, mock_uow_instance: AsyncMock
):
    # Arrange
    keyword_id = uuid.uuid4()
    user_id = "test_user_id"
    mock_uow_instance.keywords.get_by_id.return_value = None  # Simula que no se encuentra

    # Act & Assert
    with pytest.raises(
        EntityNotFoundError,
        match=f"Keyword con ID {keyword_id} no encontrada o no pertenece al usuario.",
    ):
        await get_keyword_use_case.execute(keyword_id=keyword_id, user_id=user_id)
    mock_uow_instance.keywords.get_by_id.assert_called_once_with(
        entity_id=keyword_id, user_id=user_id
    )
    mock_uow_instance.rollback.assert_called_once()  # Se espera rollback en caso de error de negocio como not found


@pytest.mark.asyncio
async def test_get_keyword_invalid_id_type(get_keyword_use_case: GetKeywordUseCase):
    # Arrange
    invalid_keyword_id = "not-a-uuid"
    user_id = "test_user_id"

    # Act & Assert
    with pytest.raises(
        ValidationError,
        match=f"El ID de la keyword debe ser un UUID válido. Valor recibido: {invalid_keyword_id}",
    ):
        await get_keyword_use_case.execute(keyword_id=invalid_keyword_id, user_id=user_id)  # type: ignore


@pytest.mark.asyncio
async def test_get_keyword_no_user_id(get_keyword_use_case: GetKeywordUseCase):
    # Arrange
    keyword_id = uuid.uuid4()
    user_id = ""  # Empty user ID

    # Act & Assert
    with pytest.raises(
        PermissionDeniedError, match="Se requiere ID de usuario para obtener una keyword"
    ):
        await get_keyword_use_case.execute(keyword_id=keyword_id, user_id=user_id)


@pytest.mark.asyncio
async def test_get_keyword_none_id(get_keyword_use_case: GetKeywordUseCase):
    # Arrange
    keyword_id = None
    user_id = "test_user_id"

    # Act & Assert
    with pytest.raises(ValidationError, match="Se requiere ID de keyword para obtenerla"):
        await get_keyword_use_case.execute(keyword_id=keyword_id, user_id=user_id)


@pytest.mark.asyncio
async def test_get_keyword_repository_generic_exception(
    get_keyword_use_case: GetKeywordUseCase, mock_uow_instance: AsyncMock
):
    # Arrange
    keyword_id = uuid.uuid4()
    user_id = "test_user_id"
    mock_uow_instance.keywords.get_by_id.side_effect = Exception("Simulated generic database error")

    # Act & Assert
    with pytest.raises(
        RepositoryError,
        match="Error inesperado en el repositorio al obtener keyword: Simulated generic database error",
    ):
        await get_keyword_use_case.execute(keyword_id=keyword_id, user_id=user_id)
    mock_uow_instance.rollback.assert_called_once()
