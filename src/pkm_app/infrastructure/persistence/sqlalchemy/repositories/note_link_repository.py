from collections.abc import Sequence
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.pkm_app.core.application.dtos.note_link_dto import (
    NoteLinkCreate,
    NoteLinkSchema,
    NoteLinkUpdate,
)
from src.pkm_app.core.application.interfaces.note_link_interface import INoteLinkRepository
from src.pkm_app.infrastructure.persistence.sqlalchemy.models import Note as NoteModel
from src.pkm_app.infrastructure.persistence.sqlalchemy.models import NoteLink as NoteLinkModel


class SQLAlchemyNoteLinkRepository(INoteLinkRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def _get_link_instance(self, link_id: UUID, user_id: str) -> NoteLinkModel | None:
        """Método helper para obtener una instancia de NoteLinkModel."""
        stmt = (
            select(NoteLinkModel)
            .where(NoteLinkModel.id == link_id, NoteLinkModel.user_id == user_id)
            .options(joinedload(NoteLinkModel.source_note), joinedload(NoteLinkModel.target_note))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def _validate_notes_exist(
        self, source_note_id: UUID, target_note_id: UUID, user_id: str
    ) -> bool:
        """Valida que ambas notas existan y pertenezcan al usuario."""
        stmt = select(NoteModel.id).where(
            NoteModel.id.in_([source_note_id, target_note_id]), NoteModel.user_id == user_id
        )
        result = await self.session.execute(stmt)
        existing_ids = {row[0] for row in result.all()}
        return len(existing_ids) == 2

    async def get_by_id(self, link_id: UUID, user_id: str) -> NoteLinkSchema | None:
        link_instance = await self._get_link_instance(link_id, user_id)
        if link_instance:
            return NoteLinkSchema.model_validate(link_instance)
        return None

    async def list_by_user(
        self, user_id: str, skip: int = 0, limit: int = 100
    ) -> list[NoteLinkSchema]:
        stmt = (
            select(NoteLinkModel)
            .where(NoteLinkModel.user_id == user_id)
            .options(joinedload(NoteLinkModel.source_note), joinedload(NoteLinkModel.target_note))
            .order_by(NoteLinkModel.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        links = result.scalars().all()
        return [NoteLinkSchema.model_validate(link) for link in links]

    async def create(self, link_in: NoteLinkCreate, user_id: str) -> NoteLinkSchema:
        # Validar que source_note_id != target_note_id
        if link_in.source_note_id == link_in.target_note_id:
            raise ValueError("Una nota no puede enlazarse consigo misma")

        # Validar que ambas notas existen y pertenecen al usuario
        notes_exist = await self._validate_notes_exist(
            link_in.source_note_id, link_in.target_note_id, user_id
        )
        if not notes_exist:
            raise ValueError("Una o ambas notas no existen o no pertenecen al usuario")

        # Verificar si ya existe un enlace similar
        existing_link = await self.get_link_between_notes(
            link_in.source_note_id, link_in.target_note_id, user_id, link_in.link_type
        )
        if existing_link:
            raise ValueError("Ya existe un enlace entre estas notas con el mismo tipo")

        link_data = link_in.model_dump()
        link_instance = NoteLinkModel(**link_data, user_id=user_id)

        try:
            self.session.add(link_instance)
            await self.session.flush()
            await self.session.refresh(link_instance)
            # Cargar las relaciones
            await self.session.refresh(
                link_instance, attribute_names=["source_note", "target_note"]
            )
            return NoteLinkSchema.model_validate(link_instance)
        except IntegrityError as e:
            await self.session.rollback()
            raise ValueError("Error de integridad al crear el enlace") from e

    async def update(
        self, link_id: UUID, link_in: NoteLinkUpdate, user_id: str
    ) -> NoteLinkSchema | None:
        link_instance = await self._get_link_instance(link_id, user_id)
        if not link_instance:
            return None

        update_data = link_in.model_dump(exclude_unset=True)

        # Si se está actualizando alguna nota, validar que existe
        if "source_note_id" in update_data or "target_note_id" in update_data:
            source_id = update_data.get("source_note_id", link_instance.source_note_id)
            target_id = update_data.get("target_note_id", link_instance.target_note_id)

            # Validar que no se enlace una nota consigo misma
            if source_id == target_id:
                raise ValueError("Una nota no puede enlazarse consigo misma")

            # Validar que las notas existen
            notes_exist = await self._validate_notes_exist(source_id, target_id, user_id)
            if not notes_exist:
                raise ValueError("Una o ambas notas no existen o no pertenecen al usuario")

        for field, value in update_data.items():
            setattr(link_instance, field, value)

        try:
            await self.session.flush()
            await self.session.refresh(link_instance)
            return NoteLinkSchema.model_validate(link_instance)
        except IntegrityError as e:
            await self.session.rollback()
            raise ValueError("Error de integridad al actualizar el enlace") from e

    async def delete(self, link_id: UUID, user_id: str) -> bool:
        link_instance = await self._get_link_instance(link_id, user_id)
        if not link_instance:
            return False

        await self.session.delete(link_instance)
        await self.session.flush()
        return True

    async def get_links_by_source_note(
        self, note_id: UUID, user_id: str, skip: int = 0, limit: int = 20
    ) -> list[NoteLinkSchema]:
        stmt = (
            select(NoteLinkModel)
            .where(NoteLinkModel.source_note_id == note_id, NoteLinkModel.user_id == user_id)
            .options(joinedload(NoteLinkModel.source_note), joinedload(NoteLinkModel.target_note))
            .order_by(NoteLinkModel.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        links = result.scalars().all()
        return [NoteLinkSchema.model_validate(link) for link in links]

    async def get_links_by_target_note(
        self, note_id: UUID, user_id: str, skip: int = 0, limit: int = 20
    ) -> list[NoteLinkSchema]:
        stmt = (
            select(NoteLinkModel)
            .where(NoteLinkModel.target_note_id == note_id, NoteLinkModel.user_id == user_id)
            .options(joinedload(NoteLinkModel.source_note), joinedload(NoteLinkModel.target_note))
            .order_by(NoteLinkModel.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        links = result.scalars().all()
        return [NoteLinkSchema.model_validate(link) for link in links]

    async def get_links_by_type(
        self, link_type: str, user_id: str, skip: int = 0, limit: int = 20
    ) -> list[NoteLinkSchema]:
        stmt = (
            select(NoteLinkModel)
            .where(NoteLinkModel.link_type == link_type, NoteLinkModel.user_id == user_id)
            .options(joinedload(NoteLinkModel.source_note), joinedload(NoteLinkModel.target_note))
            .order_by(NoteLinkModel.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        links = result.scalars().all()
        return [NoteLinkSchema.model_validate(link) for link in links]

    async def get_link_between_notes(
        self, source_note_id: UUID, target_note_id: UUID, user_id: str, link_type: str | None = None
    ) -> NoteLinkSchema | None:
        filters = [
            NoteLinkModel.source_note_id == source_note_id,
            NoteLinkModel.target_note_id == target_note_id,
            NoteLinkModel.user_id == user_id,
        ]
        if link_type:
            filters.append(NoteLinkModel.link_type == link_type)

        stmt = (
            select(NoteLinkModel)
            .where(*filters)
            .options(joinedload(NoteLinkModel.source_note), joinedload(NoteLinkModel.target_note))
        )
        result = await self.session.execute(stmt)
        link = result.scalar_one_or_none()
        if link:
            return NoteLinkSchema.model_validate(link)
        return None
