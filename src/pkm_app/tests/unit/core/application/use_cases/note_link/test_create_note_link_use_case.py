"""
Tests unitarios para CreateNoteLinkUseCase.
"""

import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock

from src.pkm_app.core.application.dtos import NoteLinkCreate, NoteLinkSchema
from src.pkm_app.core.application.use_cases.note_link.create_note_link_use_case import (
    CreateNoteLinkUseCase,
)
from src.pkm_app.core.domain.errors import PermissionDeniedError, ValidationError, RepositoryError


@pytest.mark.asyncio
class TestCreateNoteLinkUseCase:
    @pytest.fixture
    def unit_of_work(self):
        uow = MagicMock()
        uow.__aenter__ = AsyncMock(return_value=uow)
        uow.__aexit__ = AsyncMock(return_value=None)
        uow.notes.get_by_id = AsyncMock()
        uow.note_links.create = AsyncMock()
        uow.commit = AsyncMock()
        uow.rollback = AsyncMock()
        return uow

    @pytest.fixture
    def use_case(self, unit_of_work):
        return CreateNoteLinkUseCase(unit_of_work)

    @pytest.fixture
    def valid_note_link_create(self):
        return NoteLinkCreate(
            source_note_id=uuid.uuid4(),
            target_note_id=uuid.uuid4(),
            link_type="related",
            description="test",
        )

    @pytest.fixture
    def user_id(self):
        return "user-123"

    @pytest.fixture
    def note_schema(self, user_id, valid_note_link_create):
        class Note:
            def __init__(self, user_id):
                self.user_id = user_id

        return Note(user_id)

    async def test_create_success(self, use_case, unit_of_work, valid_note_link_create, user_id):
        # Mock notes.get_by_id para source y target
        note = MagicMock()
        note.user_id = user_id
        unit_of_work.notes.get_by_id.side_effect = [note, note]
        created_schema = MagicMock(spec=NoteLinkSchema)
        created_schema.id = uuid.uuid4()
        created_schema.source_note_id = valid_note_link_create.source_note_id
        created_schema.target_note_id = valid_note_link_create.target_note_id
        created_schema.link_type = valid_note_link_create.link_type
        created_schema.user_id = user_id
        unit_of_work.note_links.create.return_value = created_schema

        result = await use_case.execute(valid_note_link_create, user_id)
        assert result == created_schema
        unit_of_work.commit.assert_awaited_once()

    async def test_create_permission_denied(self, use_case, valid_note_link_create):
        with pytest.raises(PermissionDeniedError):
            await use_case.execute(valid_note_link_create, "")

    async def test_create_validation_error_missing_fields(self, use_case, unit_of_work, user_id):
        # La validación de campos requeridos ocurre al instanciar el DTO, no en el use case
        with pytest.raises(ValidationError) as exc_info:
            NoteLinkCreate()
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("source_note_id",) for e in errors)
        assert any(e["loc"] == ("target_note_id",) for e in errors)

    async def test_create_validation_error_note_not_found(
        self, use_case, unit_of_work, valid_note_link_create, user_id
    ):
        # Mock para que la primera nota no exista y la segunda sí
        note = MagicMock()
        note.user_id = user_id
        unit_of_work.notes.get_by_id = AsyncMock(side_effect=[None, note])

        with pytest.raises(ValidationError) as exc_info:
            await use_case.execute(valid_note_link_create, user_id)

        assert "no existe o no pertenece al usuario" in str(exc_info.value)
        assert exc_info.value.context["field"] == "source_note_id"

    async def test_create_repository_error(
        self, use_case, unit_of_work, valid_note_link_create, user_id
    ):
        note = MagicMock()
        note.user_id = user_id
        unit_of_work.notes.get_by_id.side_effect = [note, note]
        unit_of_work.note_links.create.side_effect = RepositoryError("DB error")
        with pytest.raises(RepositoryError):
            await use_case.execute(valid_note_link_create, user_id)
