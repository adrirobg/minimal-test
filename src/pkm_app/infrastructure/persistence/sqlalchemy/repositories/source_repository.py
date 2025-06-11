import re
from collections.abc import Sequence
from typing import Optional
from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.pkm_app.core.application.dtos.source_dto import SourceCreate, SourceSchema, SourceUpdate
from src.pkm_app.core.application.interfaces.source_interface import ISourceRepository
from src.pkm_app.infrastructure.persistence.sqlalchemy.models import Source as SourceModel


class SQLAlchemySourceRepository(ISourceRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def _get_source_instance(self, source_id: UUID, user_id: str) -> SourceModel | None:
        """Método helper para obtener una instancia de SourceModel."""
        stmt = select(SourceModel).where(
            SourceModel.id == source_id, SourceModel.user_id == user_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    def _validate_url(self, url: str) -> bool:
        """Valida que la URL tenga un formato válido."""
        if not url:
            return True
        # Patrón básico para validar URLs
        url_pattern = re.compile(
            r"^https?://"  # http:// or https://
            r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"  # domain...
            r"localhost|"  # localhost...
            r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
            r"(?::\d+)?"  # optional port
            r"(?:/?|[/?]\S+)$",
            re.IGNORECASE,
        )
        return bool(url_pattern.match(url))

    async def get_by_id(self, source_id: UUID, user_id: str) -> SourceSchema | None:
        source_instance = await self._get_source_instance(source_id, user_id)
        if source_instance:
            return SourceSchema.model_validate(source_instance)
        return None

    async def list_by_user(
        self, user_id: str, skip: int = 0, limit: int = 100
    ) -> list[SourceSchema]:
        stmt = (
            select(SourceModel)
            .where(SourceModel.user_id == user_id)
            .order_by(SourceModel.title)
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        sources = result.scalars().all()
        return [SourceSchema.model_validate(source) for source in sources]

    async def create(self, source_in: SourceCreate, user_id: str) -> SourceSchema:
        # Validar URL si se proporciona
        if source_in.url and not self._validate_url(str(source_in.url)):
            raise ValueError("El formato de la URL no es válido")

        # Verificar si ya existe una fuente con la misma URL
        if source_in.url:
            existing = await self.search_by_url(str(source_in.url), user_id)
            if existing:
                raise ValueError(f"Ya existe una fuente con la URL: {source_in.url}")

        source_data = source_in.model_dump()
        source_instance = SourceModel(**source_data, user_id=user_id)

        try:
            self.session.add(source_instance)
            await self.session.flush()
            await self.session.refresh(source_instance)
            return SourceSchema.model_validate(source_instance)
        except IntegrityError as e:
            await self.session.rollback()
            raise ValueError("Error de integridad al crear la fuente") from e

    async def update(
        self, source_id: UUID, source_in: SourceUpdate, user_id: str
    ) -> SourceSchema | None:
        source_instance = await self._get_source_instance(source_id, user_id)
        if not source_instance:
            return None

        update_data = source_in.model_dump(exclude_unset=True)

        # Validar URL si se está actualizando
        if "url" in update_data and update_data["url"]:
            if not self._validate_url(update_data["url"]):
                raise ValueError("El formato de la URL no es válido")

            # Verificar si la nueva URL ya existe para otro source
            existing = await self.search_by_url(str(update_data["url"]), user_id)
            if existing and existing.id != source_id:
                raise ValueError(f"Ya existe una fuente con la URL: {update_data['url']}")

        for field, value in update_data.items():
            setattr(source_instance, field, value)

        try:
            await self.session.flush()
            await self.session.refresh(source_instance)
            return SourceSchema.model_validate(source_instance)
        except IntegrityError as e:
            await self.session.rollback()
            raise ValueError("Error de integridad al actualizar la fuente") from e

    async def delete(self, source_id: UUID, user_id: str) -> bool:
        source_instance = await self._get_source_instance(source_id, user_id)
        if not source_instance:
            return False

        await self.session.delete(source_instance)
        await self.session.flush()
        return True

    async def search_by_type(
        self, type: str, user_id: str, skip: int = 0, limit: int = 20
    ) -> list[SourceSchema]:
        stmt = (
            select(SourceModel)
            .where(SourceModel.user_id == user_id, SourceModel.type == type)
            .order_by(SourceModel.title)
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        sources = result.scalars().all()
        return [SourceSchema.model_validate(source) for source in sources]

    async def search_by_url(self, url: str, user_id: str) -> SourceSchema | None:
        stmt = select(SourceModel).where(SourceModel.user_id == user_id, SourceModel.url == url)
        result = await self.session.execute(stmt)
        source = result.scalar_one_or_none()
        if source:
            return SourceSchema.model_validate(source)
        return None

    async def search_by_title(
        self, query: str, user_id: str, skip: int = 0, limit: int = 20
    ) -> list[SourceSchema]:
        search_term = f"%{query}%"
        stmt = (
            select(SourceModel)
            .where(
                SourceModel.user_id == user_id,
                or_(
                    SourceModel.title.ilike(search_term), SourceModel.description.ilike(search_term)
                ),
            )
            .order_by(SourceModel.title)
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        sources = result.scalars().all()
        return [SourceSchema.model_validate(source) for source in sources]
