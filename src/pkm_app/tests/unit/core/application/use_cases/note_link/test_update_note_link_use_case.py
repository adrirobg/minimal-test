"""
Tests unitarios para UpdateNoteLinkUseCase.
"""

import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock

from src.pkm_app.core.application.dtos import NoteLinkSchema, NoteLinkUpdate
from src.pkm_app.core.application.use_cases.note_link.update_note_link_use_case import (
    UpdateNoteLinkUseCase,
)
from src.pkm_app.core.domain.errors import (
    NoteLinkNotFoundError,
    PermissionDeniedError,
    RepositoryError,
    ValidationError,
)


@pytest.mark.asyncio
class TestUpdateNoteLinkUseCase:
    @pytest.fixture
    def unit_of_work(self):
        uow = MagicMock()
        uow.__aenter__ = AsyncMock(return_value=uow)
        uow.__aexit__ = AsyncMock(return_value=None)
        uow.notes.get_by_id = AsyncMock()
        uow.note_links.get_by_id = AsyncMock()
        uow.note_links.update = AsyncMock()
        uow.commit = AsyncMock()
        uow.rollback = AsyncMock()
        return uow

    @pytest.fixture
    def use_case(self, unit_of_work):
        return UpdateNoteLinkUseCase(unit_of_work)

    @pytest.fixture
    def valid_note_link_update(self):
        return NoteLinkUpdate(link_type="updated", description="updated description")

    @pytest.fixture
    def user_id(self):
        return "user-123"

    @pytest.fixture
    def existing_note_link(self, user_id):
        return NoteLinkSchema(
            id=uuid.uuid4(),
            source_note_id=uuid.uuid4(),
            target_note_id=uuid.uuid4(),
            link_type="original",
            user_id=user_id,
            created_at="2023-01-01T00:00:00",
        )

    async def test_update_success(
        self, use_case, unit_of_work, valid_note_link_update, user_id, existing_note_link
    ):
        unit_of_work.note_links.get_by_id.return_value = existing_note_link
        updated_schema = existing_note_link.model_copy(update={"link_type": "updated"})
        unit_of_work.note_links.update.return_value = updated_schema

        result = await use_case.execute(existing_note_link.id, valid_note_link_update, user_id)
        assert result == updated_schema
        unit_of_work.commit.assert_awaited_once()

    async def test_update_permission_denied(self, use_case, valid_note_link_update):
        with pytest.raises(PermissionDeniedError):
            await use_case.execute(uuid.uuid4(), valid_note_link_update, "")

    async def test_update_not_found(self, use_case, unit_of_work, valid_note_link_update, user_id):
        unit_of_work.note_links.get_by_id.return_value = None
        note_link_id = uuid.uuid4()

        with pytest.raises(NoteLinkNotFoundError):
            await use_case.execute(note_link_id, valid_note_link_update, user_id)

    async def test_update_no_changes(self, use_case, unit_of_work, user_id, existing_note_link):
        empty_update = NoteLinkUpdate()
        with pytest.raises(ValidationError):
            await use_case.execute(existing_note_link.id, empty_update, user_id)

    async def test_update_repository_error(
        self, use_case, unit_of_work, valid_note_link_update, user_id, existing_note_link
    ):
        unit_of_work.note_links.get_by_id.return_value = existing_note_link
        unit_of_work.note_links.update.side_effect = RepositoryError("DB error")

        with pytest.raises(RepositoryError):
            await use_case.execute(existing_note_link.id, valid_note_link_update, user_id)
