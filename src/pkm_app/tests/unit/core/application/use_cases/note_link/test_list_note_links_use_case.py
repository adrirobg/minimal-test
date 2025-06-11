"""
Tests unitarios para ListNoteLinksUseCase.
"""

import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock

from src.pkm_app.core.application.dtos import NoteLinkSchema
from src.pkm_app.core.application.use_cases.note_link.list_note_links_use_case import (
    ListNoteLinksUseCase,
)
from src.pkm_app.core.domain.errors import PermissionDeniedError, RepositoryError


@pytest.mark.asyncio
class TestListNoteLinksUseCase:
    @pytest.fixture
    def unit_of_work(self):
        uow = MagicMock()
        uow.__aenter__ = AsyncMock(return_value=uow)
        uow.__aexit__ = AsyncMock(return_value=None)
        uow.notes.get_by_id = AsyncMock()
        uow.note_links.list_by_user = AsyncMock()
        uow.note_links.list_by_source_note = AsyncMock()
        uow.note_links.list_by_target_note = AsyncMock()
        return uow

    @pytest.fixture
    def use_case(self, unit_of_work):
        return ListNoteLinksUseCase(unit_of_work)

    @pytest.fixture
    def user_id(self):
        return "user-123"

    @pytest.fixture
    def note_link_schemas(self, user_id):
        return [
            NoteLinkSchema(
                id=uuid.uuid4(),
                source_note_id=uuid.uuid4(),
                target_note_id=uuid.uuid4(),
                link_type="related",
                user_id=user_id,
                created_at="2023-01-01T00:00:00",
            )
        ]

    async def test_list_all_success(self, use_case, unit_of_work, user_id, note_link_schemas):
        unit_of_work.note_links.list_by_user.return_value = note_link_schemas

        result = await use_case.execute(user_id)
        assert result == note_link_schemas
        unit_of_work.note_links.list_by_user.assert_awaited_once_with(
            user_id=user_id, skip=0, limit=50
        )

    async def test_list_by_source_success(self, use_case, unit_of_work, user_id, note_link_schemas):
        source_note_id = uuid.uuid4()
        note = MagicMock()
        note.user_id = user_id
        unit_of_work.notes.get_by_id.return_value = note
        unit_of_work.note_links.list_by_source_note.return_value = note_link_schemas

        result = await use_case.execute(user_id, source_note_id=source_note_id)
        assert result == note_link_schemas
        unit_of_work.notes.get_by_id.assert_called_once_with(source_note_id)
        unit_of_work.note_links.list_by_source_note.assert_awaited_once_with(
            user_id=user_id, source_note_id=source_note_id, skip=0, limit=50
        )

    async def test_list_by_target_success(self, use_case, unit_of_work, user_id, note_link_schemas):
        target_note_id = uuid.uuid4()
        note = MagicMock()
        note.user_id = user_id
        unit_of_work.notes.get_by_id.return_value = note
        unit_of_work.note_links.list_by_target_note.return_value = note_link_schemas

        result = await use_case.execute(user_id, target_note_id=target_note_id)
        assert result == note_link_schemas
        unit_of_work.notes.get_by_id.assert_called_once_with(target_note_id)
        unit_of_work.note_links.list_by_target_note.assert_awaited_once_with(
            user_id=user_id, target_note_id=target_note_id, skip=0, limit=50
        )

    async def test_list_permission_denied(self, use_case):
        with pytest.raises(PermissionDeniedError):
            await use_case.execute("")

    async def test_list_repository_error(self, use_case, unit_of_work, user_id):
        unit_of_work.note_links.list_by_user = AsyncMock(side_effect=RepositoryError("DB error"))
        unit_of_work.rollback = AsyncMock()

        with pytest.raises(RepositoryError):
            await use_case.execute(user_id)
        unit_of_work.note_links.list_by_user.assert_awaited_once_with(
            user_id=user_id, skip=0, limit=50
        )
        unit_of_work.rollback.assert_awaited_once()
