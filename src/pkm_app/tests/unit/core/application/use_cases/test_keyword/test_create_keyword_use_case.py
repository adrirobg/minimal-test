import uuid
from unittest.mock import AsyncMock
import pytest
from src.pkm_app.core.application.dtos import KeywordCreate, KeywordSchema
from src.pkm_app.core.application.use_cases.keyword.create_keyword_use_case import (
    CreateKeywordUseCase,
)
from src.pkm_app.core.domain.errors import PermissionDeniedError, ValidationError, RepositoryError


@pytest.fixture
def mock_uow_instance():
    mock = AsyncMock()
    mock_keywords_repo = AsyncMock()  # Renombrado para claridad
    mock.keywords = mock_keywords_repo
    mock.__aenter__.return_value = mock  # Para el context manager asíncrono
    return mock


@pytest.fixture
def create_keyword_use_case(mock_uow_instance):
    return CreateKeywordUseCase(unit_of_work=mock_uow_instance)


@pytest.mark.asyncio
async def test_create_keyword_success(
    create_keyword_use_case: CreateKeywordUseCase, mock_uow_instance: AsyncMock
):
    # Arrange
    keyword_data = KeywordCreate(name="Test Keyword")
    user_id = "test_user_id"
    from datetime import datetime

    expected_keyword_id = uuid.uuid4()
    expected_keyword = KeywordSchema(
        id=expected_keyword_id, name="Test Keyword", user_id=user_id, created_at=datetime.now()
    )
    mock_uow_instance.keywords.create.return_value = expected_keyword

    # Act
    result = await create_keyword_use_case.execute(keyword_in=keyword_data, user_id=user_id)

    # Assert
    mock_uow_instance.keywords.create.assert_called_once_with(
        keyword_in=keyword_data, user_id=user_id
    )
    mock_uow_instance.commit.assert_called_once()
    assert result == expected_keyword


@pytest.mark.asyncio
async def test_create_keyword_no_user_id(create_keyword_use_case: CreateKeywordUseCase):
    # Arrange
    keyword_data = KeywordCreate(name="Test Keyword")
    user_id = ""  # Empty user ID

    # Act & Assert
    with pytest.raises(
        PermissionDeniedError, match="Se requiere ID de usuario para crear una keyword."
    ):
        await create_keyword_use_case.execute(keyword_in=keyword_data, user_id=user_id)


def test_create_keyword_empty_name():
    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        KeywordCreate(name="")
    assert "El nombre de la keyword no puede estar vacío." in str(exc_info.value)


def test_create_keyword_name_with_only_spaces():
    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        KeywordCreate(name="   ")
    assert "El nombre de la keyword no puede estar vacío." in str(exc_info.value)


@pytest.mark.asyncio
async def test_create_keyword_repository_value_error(
    create_keyword_use_case: CreateKeywordUseCase, mock_uow_instance: AsyncMock
):
    # Arrange
    keyword_data = KeywordCreate(name="Test Keyword")
    user_id = "test_user_id"
    mock_uow_instance.keywords.create.side_effect = ValueError(
        "Simulated repository validation error (e.g., duplicate name)"
    )

    # Act & Assert
    with pytest.raises(
        ValidationError, match="Error al crear la keyword: Simulated repository validation error"
    ):
        await create_keyword_use_case.execute(keyword_in=keyword_data, user_id=user_id)
    mock_uow_instance.rollback.assert_called_once()
    mock_uow_instance.commit.assert_not_called()


@pytest.mark.asyncio
async def test_create_keyword_generic_exception(
    create_keyword_use_case: CreateKeywordUseCase, mock_uow_instance: AsyncMock
):
    # Arrange
    keyword_data = KeywordCreate(name="Test Keyword")
    user_id = "test_user_id"
    mock_uow_instance.keywords.create.side_effect = Exception("Simulated generic database error")

    # Act & Assert
    with pytest.raises(
        RepositoryError,
        match="Error inesperado en el repositorio al crear keyword: Simulated generic database error",
    ):
        await create_keyword_use_case.execute(keyword_in=keyword_data, user_id=user_id)
    mock_uow_instance.rollback.assert_called_once()
    mock_uow_instance.commit.assert_not_called()
