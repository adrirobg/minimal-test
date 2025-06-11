"""
Tests unitarios para DeleteNoteLinkUseCase.
"""

import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock

from src.pkm_app.core.application.use_cases.note_link.delete_note_link_use_case import (
    DeleteNoteLinkUseCase,
)
from src.pkm_app.core.domain.errors import (
    NoteLinkNotFoundError,
    PermissionDeniedError,
    RepositoryError,
)


@pytest.mark.asyncio
class TestDeleteNoteLinkUseCase:
    @pytest.fixture
    def unit_of_work(self):
        uow = MagicMock()
        uow.__aenter__ = AsyncMock(return_value=uow)
        uow.__aexit__ = AsyncMock(return_value=None)
        uow.note_links.delete = AsyncMock()
        uow.commit = AsyncMock()
        uow.rollback = AsyncMock()
        return uow

    @pytest.fixture
    def use_case(self, unit_of_work):
        return DeleteNoteLinkUseCase(unit_of_work)

    @pytest.fixture
    def user_id(self):
        return "user-123"

    async def test_delete_success(self, use_case, unit_of_work, user_id):
        note_link_id = uuid.uuid4()
        unit_of_work.note_links.delete.return_value = True

        result = await use_case.execute(note_link_id, user_id)
        assert result is True
        unit_of_work.commit.assert_awaited_once()

    async def test_delete_permission_denied(self, use_case):
        with pytest.raises(PermissionDeniedError):
            await use_case.execute(uuid.uuid4(), "")

    async def test_delete_not_found(self, use_case, unit_of_work, user_id):
        unit_of_work.note_links.delete.side_effect = NoteLinkNotFoundError("Not found")
        note_link_id = uuid.uuid4()

        with pytest.raises(NoteLinkNotFoundError):
            await use_case.execute(note_link_id, user_id)

    async def test_delete_repository_error(self, use_case, unit_of_work, user_id):
        unit_of_work.note_links.delete.side_effect = RepositoryError("DB error")
        note_link_id = uuid.uuid4()

        with pytest.raises(RepositoryError):
            await use_case.execute(note_link_id, user_id)
