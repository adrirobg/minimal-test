from collections.abc import Sequence
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.pkm_app.core.application.dtos.keyword_dto import (
    KeywordCreate,
    KeywordSchema,
    KeywordUpdate,
)
from src.pkm_app.core.application.interfaces.keyword_interface import IKeywordRepository
from src.pkm_app.infrastructure.persistence.sqlalchemy.models import Keyword as KeywordModel


class SQLAlchemyKeywordRepository(IKeywordRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def _get_keyword_instance(self, keyword_id: UUID, user_id: str) -> KeywordModel | None:
        """Método helper para obtener una instancia de KeywordModel."""
        stmt = select(KeywordModel).where(
            KeywordModel.id == keyword_id, KeywordModel.user_id == user_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id(self, keyword_id: UUID, user_id: str) -> KeywordSchema | None:
        keyword_instance = await self._get_keyword_instance(keyword_id, user_id)
        if keyword_instance:
            return KeywordSchema.model_validate(keyword_instance)
        return None

    async def list_by_user(
        self, user_id: str, skip: int = 0, limit: int = 100
    ) -> list[KeywordSchema]:
        stmt = (
            select(KeywordModel)
            .where(KeywordModel.user_id == user_id)
            .order_by(KeywordModel.name)
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        keywords = result.scalars().all()
        return [KeywordSchema.model_validate(keyword) for keyword in keywords]

    async def create(self, keyword_in: KeywordCreate, user_id: str) -> KeywordSchema:
        # Verificar si ya existe un keyword con el mismo nombre para este usuario
        existing = await self.get_by_name(keyword_in.name, user_id)
        if existing:
            raise ValueError(
                f"Ya existe un keyword con el nombre '{keyword_in.name}' para este usuario"
            )

        keyword_data = keyword_in.model_dump()
        keyword_instance = KeywordModel(**keyword_data, user_id=user_id)

        try:
            self.session.add(keyword_instance)
            await self.session.flush()
            await self.session.refresh(keyword_instance)
            return KeywordSchema.model_validate(keyword_instance)
        except IntegrityError as e:
            await self.session.rollback()
            raise ValueError(f"Error de integridad al crear el keyword: {keyword_in.name}") from e

    async def update(
        self, keyword_id: UUID, keyword_in: KeywordUpdate, user_id: str
    ) -> KeywordSchema | None:
        keyword_instance = await self._get_keyword_instance(keyword_id, user_id)
        if not keyword_instance:
            return None

        # Si se está actualizando el nombre, verificar que no exista otro keyword con ese nombre
        if keyword_in.name and keyword_in.name != keyword_instance.name:
            existing = await self.get_by_name(keyword_in.name, user_id)
            if existing:
                raise ValueError(
                    f"Ya existe un keyword con el nombre '{keyword_in.name}' para este usuario"
                )

        update_data = keyword_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(keyword_instance, field, value)

        try:
            await self.session.flush()
            await self.session.refresh(keyword_instance)
            return KeywordSchema.model_validate(keyword_instance)
        except IntegrityError as e:
            await self.session.rollback()
            raise ValueError("Error de integridad al actualizar el keyword") from e

    async def delete(self, keyword_id: UUID, user_id: str) -> bool:
        keyword_instance = await self._get_keyword_instance(keyword_id, user_id)
        if not keyword_instance:
            return False

        await self.session.delete(keyword_instance)
        await self.session.flush()
        return True

    async def get_by_name(self, name: str, user_id: str) -> KeywordSchema | None:
        stmt = select(KeywordModel).where(
            KeywordModel.name == name, KeywordModel.user_id == user_id
        )
        result = await self.session.execute(stmt)
        keyword = result.scalar_one_or_none()
        if keyword:
            return KeywordSchema.model_validate(keyword)
        return None
