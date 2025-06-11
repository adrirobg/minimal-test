import uuid
from unittest.mock import AsyncMock, MagicMock
import pytest

from src.pkm_app.core.application.dtos import KeywordSchema  # Necesario para mockear get_by_id
from src.pkm_app.core.application.use_cases.keyword.delete_keyword_use_case import (
    DeleteKeywordUseCase,
)
from src.pkm_app.core.domain.errors import (
    EntityNotFoundError,
    PermissionDeniedError,
    ValidationError,
    RepositoryError,
    BusinessRuleViolationError,
)


@pytest.fixture
def mock_uow_instance():
    mock = AsyncMock()
    mock_keywords_repo = AsyncMock()
    mock.keywords = mock_keywords_repo
    mock.__aenter__.return_value = mock
    return mock


@pytest.fixture
def delete_keyword_use_case(mock_uow_instance):
    return DeleteKeywordUseCase(unit_of_work=mock_uow_instance)


@pytest.mark.asyncio
async def test_delete_keyword_success(
    delete_keyword_use_case: DeleteKeywordUseCase, mock_uow_instance: AsyncMock
):
    # Arrange
    keyword_id = uuid.uuid4()
    user_id = "test_user_id"

    # Mockear la keyword existente que se recupera primero
    from datetime import datetime

    existing_keyword_mock = KeywordSchema(
        id=keyword_id, name="Test Keyword", user_id=user_id, created_at=datetime.now()
    )
    mock_uow_instance.keywords.get_by_id.return_value = existing_keyword_mock
    mock_uow_instance.keywords.delete.return_value = (
        True  # El repo.delete devuelve True si tiene éxito
    )

    # Act
    result = await delete_keyword_use_case.execute(keyword_id=keyword_id, user_id=user_id)

    # Assert
    mock_uow_instance.keywords.get_by_id.assert_called_once_with(
        entity_id=keyword_id, user_id=user_id
    )
    mock_uow_instance.keywords.delete.assert_called_once_with(entity_id=keyword_id, user_id=user_id)
    mock_uow_instance.commit.assert_called_once()
    assert result is True


@pytest.mark.asyncio
async def test_delete_keyword_not_found_at_get(
    delete_keyword_use_case: DeleteKeywordUseCase, mock_uow_instance: AsyncMock
):
    # Arrange
    keyword_id = uuid.uuid4()
    user_id = "test_user_id"
    mock_uow_instance.keywords.get_by_id.return_value = None  # No se encuentra al buscarla primero

    # Act & Assert
    with pytest.raises(
        EntityNotFoundError,
        match=f"Keyword con ID {keyword_id} no encontrada o no pertenece al usuario.",
    ):
        await delete_keyword_use_case.execute(keyword_id=keyword_id, user_id=user_id)

    mock_uow_instance.keywords.get_by_id.assert_called_once_with(
        entity_id=keyword_id, user_id=user_id
    )
    mock_uow_instance.keywords.delete.assert_not_called()
    mock_uow_instance.rollback.assert_called_once()
    mock_uow_instance.commit.assert_not_called()


@pytest.mark.asyncio
async def test_delete_keyword_not_found_at_delete_method(
    delete_keyword_use_case: DeleteKeywordUseCase, mock_uow_instance: AsyncMock
):
    # Arrange
    keyword_id = uuid.uuid4()
    user_id = "test_user_id"
    from datetime import datetime

    existing_keyword_mock = KeywordSchema(
        id=keyword_id, name="Test Keyword", user_id=user_id, created_at=datetime.now()
    )
    mock_uow_instance.keywords.get_by_id.return_value = existing_keyword_mock
    # El método delete del repo devuelve False en lugar de lanzar EntityNotFoundError
    mock_uow_instance.keywords.delete.return_value = False

    # Act & Assert
    with pytest.raises(
        EntityNotFoundError, match=f"Keyword con ID {keyword_id} no pudo ser eliminada"
    ):
        await delete_keyword_use_case.execute(keyword_id=keyword_id, user_id=user_id)

    mock_uow_instance.keywords.get_by_id.assert_called_once_with(
        entity_id=keyword_id, user_id=user_id
    )
    mock_uow_instance.keywords.delete.assert_called_once_with(entity_id=keyword_id, user_id=user_id)
    mock_uow_instance.rollback.assert_called_once()  # Rollback porque la entidad no se eliminó como se esperaba
    mock_uow_instance.commit.assert_not_called()


@pytest.mark.asyncio
async def test_delete_keyword_no_user_id(delete_keyword_use_case: DeleteKeywordUseCase):
    # Arrange
    keyword_id = uuid.uuid4()
    user_id = ""  # Empty user ID

    # Act & Assert
    with pytest.raises(
        PermissionDeniedError, match="Se requiere ID de usuario para eliminar una keyword"
    ):
        await delete_keyword_use_case.execute(keyword_id=keyword_id, user_id=user_id)


@pytest.mark.asyncio
async def test_delete_keyword_none_id(delete_keyword_use_case: DeleteKeywordUseCase):
    # Arrange
    keyword_id = None
    user_id = "test_user_id"

    # Act & Assert
    with pytest.raises(ValidationError, match="Se requiere ID de keyword para eliminarla"):
        await delete_keyword_use_case.execute(keyword_id=keyword_id, user_id=user_id)


@pytest.mark.asyncio
async def test_delete_keyword_invalid_id_type(delete_keyword_use_case: DeleteKeywordUseCase):
    # Arrange
    invalid_keyword_id = "not-a-uuid"
    user_id = "test_user_id"

    # Act & Assert
    with pytest.raises(
        ValidationError,
        match=f"El ID de la keyword debe ser un UUID válido. Valor recibido: {invalid_keyword_id}",
    ):
        await delete_keyword_use_case.execute(keyword_id=invalid_keyword_id, user_id=user_id)  # type: ignore


@pytest.mark.asyncio
async def test_delete_keyword_unauthorized_different_user(
    delete_keyword_use_case: DeleteKeywordUseCase, mock_uow_instance: AsyncMock
):
    # Arrange
    keyword_id = uuid.uuid4()
    # owner_user_id = "owner_user_id" # No es necesario para este test si get_by_id devuelve None
    attacker_user_id = "attacker_user_id"
    mock_uow_instance.keywords.get_by_id.return_value = None  # Simula que no pertenece al attacker

    # Act & Assert
    with pytest.raises(
        EntityNotFoundError,
        match=f"Keyword con ID {keyword_id} no encontrada o no pertenece al usuario.",
    ):
        await delete_keyword_use_case.execute(keyword_id=keyword_id, user_id=attacker_user_id)

    mock_uow_instance.keywords.get_by_id.assert_called_once_with(
        entity_id=keyword_id, user_id=attacker_user_id
    )
    mock_uow_instance.rollback.assert_called_once()


@pytest.mark.asyncio
async def test_delete_keyword_with_notes_raises_business_rule_violation(
    delete_keyword_use_case: DeleteKeywordUseCase, mock_uow_instance: AsyncMock
):
    # Arrange
    keyword_id = uuid.uuid4()
    user_id = "test_user_id"

    from datetime import datetime

    existing_keyword_mock = KeywordSchema(
        id=keyword_id, name="Test Keyword", user_id=user_id, created_at=datetime.now()
    )
    mock_uow_instance.keywords.get_by_id.return_value = existing_keyword_mock

    # El repositorio delete debe lanzar BusinessRuleViolationError si la keyword está asociada a notas
    error_message = f"La keyword {keyword_id} no puede ser eliminada porque está asociada a notas."
    mock_uow_instance.keywords.delete.side_effect = BusinessRuleViolationError(error_message)

    # Act & Assert
    with pytest.raises(BusinessRuleViolationError, match=error_message):
        await delete_keyword_use_case.execute(keyword_id=keyword_id, user_id=user_id)

    mock_uow_instance.keywords.get_by_id.assert_called_once_with(
        entity_id=keyword_id, user_id=user_id
    )
    mock_uow_instance.keywords.delete.assert_called_once_with(entity_id=keyword_id, user_id=user_id)
    mock_uow_instance.rollback.assert_called_once()
    mock_uow_instance.commit.assert_not_called()


@pytest.mark.asyncio
async def test_delete_keyword_repository_generic_exception(
    delete_keyword_use_case: DeleteKeywordUseCase, mock_uow_instance: AsyncMock
):
    # Arrange
    keyword_id = uuid.uuid4()
    user_id = "test_user_id"

    from datetime import datetime

    existing_keyword_mock = KeywordSchema(
        id=keyword_id, name="Test Keyword", user_id=user_id, created_at=datetime.now()
    )
    mock_uow_instance.keywords.get_by_id.return_value = existing_keyword_mock
    mock_uow_instance.keywords.delete.side_effect = Exception("Simulated generic database error")

    # Act & Assert
    with pytest.raises(
        RepositoryError,
        match="Error inesperado en el repositorio al eliminar keyword: Simulated generic database error",
    ):
        await delete_keyword_use_case.execute(keyword_id=keyword_id, user_id=user_id)

    mock_uow_instance.rollback.assert_called_once()
    mock_uow_instance.commit.assert_not_called()
