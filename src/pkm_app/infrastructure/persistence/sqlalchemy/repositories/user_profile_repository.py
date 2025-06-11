from collections.abc import Sequence
from typing import Optional

from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.pkm_app.core.application.dtos.user_profile_dto import (
    UserProfileCreate,
    UserProfileSchema,
    UserProfileUpdate,
)
from src.pkm_app.core.application.interfaces.user_profile_interface import IUserProfileRepository
from src.pkm_app.infrastructure.persistence.sqlalchemy.models import UserProfile as UserProfileModel


class SQLAlchemyUserProfileRepository(IUserProfileRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def _get_profile_instance(self, user_id: str) -> UserProfileModel | None:
        """Método helper para obtener una instancia de UserProfileModel."""
        stmt = select(UserProfileModel).where(UserProfileModel.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: str) -> UserProfileSchema | None:
        profile_instance = await self._get_profile_instance(user_id)
        if profile_instance:
            return UserProfileSchema.model_validate(profile_instance)
        return None

    async def get_by_email(self, email: str) -> UserProfileSchema | None:
        stmt = select(UserProfileModel).where(UserProfileModel.email == email)
        result = await self.session.execute(stmt)
        profile = result.scalar_one_or_none()
        if profile:
            return UserProfileSchema.model_validate(profile)
        return None

    async def list_all(self, skip: int = 0, limit: int = 100) -> list[UserProfileSchema]:
        stmt = select(UserProfileModel).order_by(UserProfileModel.name).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        profiles = result.scalars().all()
        return [UserProfileSchema.model_validate(profile) for profile in profiles]

    async def create(self, profile_in: UserProfileCreate) -> UserProfileSchema:
        # Validar email único si se proporciona
        if profile_in.email:
            existing = await self.get_by_email(profile_in.email)
            if existing:
                raise ValueError(f"Ya existe un usuario con el email: {profile_in.email}")

        profile_data = profile_in.model_dump()
        profile_instance = UserProfileModel(**profile_data)

        try:
            self.session.add(profile_instance)
            await self.session.flush()
            await self.session.refresh(profile_instance)
            return UserProfileSchema.model_validate(profile_instance)
        except IntegrityError as e:
            await self.session.rollback()
            raise ValueError("Error de integridad al crear el perfil de usuario") from e

    async def update(self, user_id: str, profile_in: UserProfileUpdate) -> UserProfileSchema | None:
        profile_instance = await self._get_profile_instance(user_id)
        if not profile_instance:
            return None

        update_data = profile_in.model_dump(exclude_unset=True)

        # Validar email único si se está actualizando
        if "email" in update_data and update_data["email"]:
            existing = await self.get_by_email(update_data["email"])
            if existing and existing.user_id != user_id:
                raise ValueError(f"Ya existe un usuario con el email: {update_data['email']}")

        for field, value in update_data.items():
            setattr(profile_instance, field, value)

        try:
            await self.session.flush()
            await self.session.refresh(profile_instance)
            return UserProfileSchema.model_validate(profile_instance)
        except IntegrityError as e:
            await self.session.rollback()
            raise ValueError("Error de integridad al actualizar el perfil de usuario") from e

    async def delete(self, user_id: str) -> bool:
        profile_instance = await self._get_profile_instance(user_id)
        if not profile_instance:
            return False

        await self.session.delete(profile_instance)
        await self.session.flush()
        return True

    async def search_by_name(
        self, query: str, skip: int = 0, limit: int = 20
    ) -> list[UserProfileSchema]:
        search_term = f"%{query}%"
        stmt = (
            select(UserProfileModel)
            .where(UserProfileModel.name.ilike(search_term))
            .order_by(UserProfileModel.name)
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        profiles = result.scalars().all()
        return [UserProfileSchema.model_validate(profile) for profile in profiles]
