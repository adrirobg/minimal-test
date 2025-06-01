import uuid
from unittest.mock import AsyncMock, MagicMock
import pytest

from src.pkm_app.core.application.dtos import KeywordSchema, KeywordUpdate
from src.pkm_app.core.application.use_cases.keyword.update_keyword_use_case import (
    UpdateKeywordUseCase,
)
from src.pkm_app.core.domain.errors import (
    EntityNotFoundError,
    PermissionDeniedError,
    ValidationError,
    RepositoryError,
)


@pytest.fixture
def mock_uow_instance():
    mock = AsyncMock()
    mock_keywords_repo = AsyncMock()
    mock.keywords = mock_keywords_repo
    mock.__aenter__.return_value = mock
    return mock


@pytest.fixture
def update_keyword_use_case(mock_uow_instance):
    return UpdateKeywordUseCase(unit_of_work=mock_uow_instance)


@pytest.mark.asyncio
async def test_update_keyword_success(
    update_keyword_use_case: UpdateKeywordUseCase, mock_uow_instance: AsyncMock
):
    # Arrange
    keyword_id = uuid.uuid4()
    user_id = "test_user_id"
    keyword_update_data = KeywordUpdate(name="Updated Keyword Name")

    # Mockear la keyword existente que se recupera primero
    from datetime import datetime
    existing_keyword_mock = KeywordSchema(
        id=keyword_id,
        name="Old Keyword Name",
        user_id=user_id,
        created_at=datetime.now()
    )
    mock_uow_instance.keywords.get_by_id.return_value = existing_keyword_mock

    # Mockear la keyword actualizada que devuelve el método update del repo
    updated_keyword_schema = KeywordSchema(
        id=keyword_id,
        name="Updated Keyword Name",
        user_id=user_id,
        created_at=datetime.now()
    )
    mock_uow_instance.keywords.update.return_value = updated_keyword_schema

    # Act
    result = await update_keyword_use_case.execute(
        keyword_id=keyword_id, keyword_in=keyword_update_data, user_id=user_id
    )

    # Assert
    mock_uow_instance.keywords.get_by_id.assert_called_once_with(
        entity_id=keyword_id, user_id=user_id
    )
    mock_uow_instance.keywords.update.assert_called_once_with(
        entity_id=keyword_id, entity_in=keyword_update_data, user_id=user_id
    )
    mock_uow_instance.commit.assert_called_once()
    assert result == updated_keyword_schema
    assert result.name == "Updated Keyword Name"


@pytest.mark.asyncio
async def test_update_keyword_not_found_at_get(
    update_keyword_use_case: UpdateKeywordUseCase, mock_uow_instance: AsyncMock
):
    # Arrange
    keyword_id = uuid.uuid4()
    user_id = "test_user_id"
    keyword_update_data = KeywordUpdate(name="Updated Name")
    mock_uow_instance.keywords.get_by_id.return_value = None  # No se encuentra al buscarla primero

    # Act & Assert
    with pytest.raises(
        EntityNotFoundError,
        match=f"Keyword con ID {keyword_id} no encontrada o no pertenece al usuario.",
    ):
        await update_keyword_use_case.execute(
            keyword_id=keyword_id, keyword_in=keyword_update_data, user_id=user_id
        )

    mock_uow_instance.keywords.get_by_id.assert_called_once_with(
        entity_id=keyword_id, user_id=user_id
    )
    mock_uow_instance.keywords.update.assert_not_called()  # No se debe llamar a update si no se encuentra
    mock_uow_instance.rollback.assert_called_once()
    mock_uow_instance.commit.assert_not_called()


@pytest.mark.asyncio
async def test_update_keyword_not_found_at_update(
    update_keyword_use_case: UpdateKeywordUseCase, mock_uow_instance: AsyncMock
):
    # Arrange
    keyword_id = uuid.uuid4()
    user_id = "test_user_id"
    keyword_update_data = KeywordUpdate(name="Updated Name")

    from datetime import datetime
    existing_keyword_mock = KeywordSchema(
        id=keyword_id,
        name="Old Name",
        user_id=user_id,
        created_at=datetime.now()
    )
    mock_uow_instance.keywords.get_by_id.return_value = existing_keyword_mock
    mock_uow_instance.keywords.update.return_value = None  # El repo.update devuelve None

    # Act & Assert
    with pytest.raises(
        EntityNotFoundError,
        match=f"Keyword con ID {keyword_id} no encontrada durante la actualización.",
    ):
        await update_keyword_use_case.execute(
            keyword_id=keyword_id, keyword_in=keyword_update_data, user_id=user_id
        )

    mock_uow_instance.keywords.get_by_id.assert_called_once_with(
        entity_id=keyword_id, user_id=user_id
    )
    mock_uow_instance.keywords.update.assert_called_once_with(
        entity_id=keyword_id, entity_in=keyword_update_data, user_id=user_id
    )
    mock_uow_instance.rollback.assert_called_once()
    mock_uow_instance.commit.assert_not_called()


def test_update_keyword_empty_name():
    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        KeywordUpdate(name="")
    assert "El nombre de la keyword no puede estar vacío." in str(exc_info.value)


def test_update_keyword_name_with_only_spaces():
    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        KeywordUpdate(name="   ")
    assert "El nombre de la keyword no puede estar vacío." in str(exc_info.value)


@pytest.mark.asyncio
async def test_update_keyword_no_user_id(update_keyword_use_case: UpdateKeywordUseCase):
    # Arrange
    keyword_id = uuid.uuid4()
    keyword_update_data = KeywordUpdate(name="Some Name")
    user_id = ""  # Empty user ID

    # Act & Assert
    with pytest.raises(
        PermissionDeniedError, match="Se requiere ID de usuario para actualizar una keyword"
    ):
        await update_keyword_use_case.execute(
            keyword_id=keyword_id, keyword_in=keyword_update_data, user_id=user_id
        )


@pytest.mark.asyncio
async def test_update_keyword_none_id(update_keyword_use_case: UpdateKeywordUseCase):
    # Arrange
    keyword_id = None
    keyword_update_data = KeywordUpdate(name="Some Name")
    user_id = "test_user_id"

    # Act & Assert
    with pytest.raises(ValidationError, match="Se requiere ID de keyword para actualizarla"):
        await update_keyword_use_case.execute(
            keyword_id=keyword_id, keyword_in=keyword_update_data, user_id=user_id
        )


@pytest.mark.asyncio
async def test_update_keyword_invalid_id_type(update_keyword_use_case: UpdateKeywordUseCase):
    # Arrange
    invalid_keyword_id = "not-a-uuid"
    user_id = "test_user_id"
    keyword_update_data = KeywordUpdate(name="Some Name")

    # Act & Assert
    with pytest.raises(
        ValidationError,
        match=f"El ID de la keyword debe ser un UUID válido. Valor recibido: {invalid_keyword_id}",
    ):
        await update_keyword_use_case.execute(keyword_id=invalid_keyword_id, keyword_in=keyword_update_data, user_id=user_id)  # type: ignore


@pytest.mark.asyncio
async def test_update_keyword_unauthorized_different_user(
    update_keyword_use_case: UpdateKeywordUseCase, mock_uow_instance: AsyncMock
):
    # Arrange
    keyword_id = uuid.uuid4()
    owner_user_id = "owner_user_id"
    attacker_user_id = "attacker_user_id"  # Usuario diferente
    keyword_update_data = KeywordUpdate(name="Updated Name")

    # Simula que get_by_id con attacker_user_id no encuentra la keyword (o lanza PermissionDeniedError desde el repo)
    mock_uow_instance.keywords.get_by_id.return_value = None
    # Opcionalmente, si el repo lanzara PermissionDeniedError directamente:
    # mock_uow_instance.keywords.get_by_id.side_effect = PermissionDeniedError("User does not own this keyword")

    # Act & Assert
    # El error esperado es EntityNotFoundError porque get_by_id devuelve None
    with pytest.raises(
        EntityNotFoundError,
        match=f"Keyword con ID {keyword_id} no encontrada o no pertenece al usuario.",
    ):
        await update_keyword_use_case.execute(
            keyword_id=keyword_id, keyword_in=keyword_update_data, user_id=attacker_user_id
        )

    mock_uow_instance.keywords.get_by_id.assert_called_once_with(
        entity_id=keyword_id, user_id=attacker_user_id
    )
    mock_uow_instance.rollback.assert_called_once()


@pytest.mark.asyncio
async def test_update_keyword_repository_value_error_on_update(
    update_keyword_use_case: UpdateKeywordUseCase, mock_uow_instance: AsyncMock
):
    # Arrange
    keyword_id = uuid.uuid4()
    user_id = "test_user_id"
    keyword_update_data = KeywordUpdate(name="Duplicate Name")

    from datetime import datetime
    existing_keyword_mock = KeywordSchema(
        id=keyword_id,
        name="Old Name",
        user_id=user_id,
        created_at=datetime.now()
    )
    mock_uow_instance.keywords.get_by_id.return_value = existing_keyword_mock
    mock_uow_instance.keywords.update.side_effect = ValueError(
        "Simulated duplicate name error from repo"
    )

    # Act & Assert
    with pytest.raises(
        ValidationError,
        match="Error de validación al actualizar keyword: Simulated duplicate name error from repo",
    ):
        await update_keyword_use_case.execute(
            keyword_id=keyword_id, keyword_in=keyword_update_data, user_id=user_id
        )

    mock_uow_instance.rollback.assert_called_once()
    mock_uow_instance.commit.assert_not_called()


@pytest.mark.asyncio
async def test_update_keyword_generic_exception_on_update(
    update_keyword_use_case: UpdateKeywordUseCase, mock_uow_instance: AsyncMock
):
    # Arrange
    keyword_id = uuid.uuid4()
    user_id = "test_user_id"
    keyword_update_data = KeywordUpdate(name="Some Name")

    from datetime import datetime
    existing_keyword_mock = KeywordSchema(
        id=keyword_id,
        name="Old Name",
        user_id=user_id,
        created_at=datetime.now()
    )
    mock_uow_instance.keywords.get_by_id.return_value = existing_keyword_mock
    mock_uow_instance.keywords.update.side_effect = Exception("Simulated generic database error")

    # Act & Assert
    with pytest.raises(
        RepositoryError,
        match="Error inesperado en el repositorio al actualizar keyword: Simulated generic database error",
    ):
        await update_keyword_use_case.execute(
            keyword_id=keyword_id, keyword_in=keyword_update_data, user_id=user_id
        )

    mock_uow_instance.rollback.assert_called_once()
    mock_uow_instance.commit.assert_not_called()
