"""
Tests unitarios para GetNoteLinkUseCase.
"""

import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock

from src.pkm_app.core.application.dtos import NoteLinkSchema
from src.pkm_app.core.application.use_cases.note_link.get_note_link_use_case import (
    GetNoteLinkUseCase,
)
from src.pkm_app.core.domain.errors import (
    NoteLinkNotFoundError,
    PermissionDeniedError,
    RepositoryError,
)


@pytest.mark.asyncio
class TestGetNoteLinkUseCase:
    @pytest.fixture
    def unit_of_work(self):
        uow = MagicMock()
        uow.__aenter__ = AsyncMock(return_value=uow)
        uow.__aexit__ = AsyncMock(return_value=None)
        uow.note_links.get_by_id = AsyncMock()
        return uow

    @pytest.fixture
    def use_case(self, unit_of_work):
        return GetNoteLinkUseCase(unit_of_work)

    @pytest.fixture
    def user_id(self):
        return "user-123"

    @pytest.fixture
    def note_link_schema(self, user_id):
        return NoteLinkSchema(
            id=uuid.uuid4(),
            source_note_id=uuid.uuid4(),
            target_note_id=uuid.uuid4(),
            link_type="related",
            user_id=user_id,
            created_at="2023-01-01T00:00:00",
        )

    async def test_get_success(self, use_case, unit_of_work, note_link_schema, user_id):
        unit_of_work.note_links.get_by_id.return_value = note_link_schema

        result = await use_case.execute(note_link_schema.id, user_id)
        assert result == note_link_schema
        unit_of_work.note_links.get_by_id.assert_awaited_once_with(note_link_schema.id, user_id)

    async def test_get_permission_denied(self, use_case):
        with pytest.raises(PermissionDeniedError):
            await use_case.execute(uuid.uuid4(), "")

    async def test_get_not_found(self, use_case, unit_of_work, user_id):
        # Configurar mock async para el repositorio
        unit_of_work.note_links.get_by_id = AsyncMock(return_value=None)
        # Configurar mock async para rollback
        unit_of_work.rollback = AsyncMock()

        note_link_id = uuid.uuid4()

        with pytest.raises(NoteLinkNotFoundError) as exc_info:
            await use_case.execute(note_link_id, user_id)

        assert str(note_link_id) in str(exc_info.value)
        unit_of_work.note_links.get_by_id.assert_awaited_once_with(note_link_id, user_id)
        unit_of_work.rollback.assert_awaited_once()

    async def test_get_repository_error(self, use_case, unit_of_work, user_id):
        unit_of_work.note_links.get_by_id = AsyncMock(side_effect=RepositoryError("DB error"))
        unit_of_work.rollback = AsyncMock()
        note_link_id = uuid.uuid4()

        with pytest.raises(RepositoryError):
            await use_case.execute(note_link_id, user_id)
        unit_of_work.note_links.get_by_id.assert_awaited_once_with(note_link_id, user_id)
        unit_of_work.rollback.assert_awaited_once()
