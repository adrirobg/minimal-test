import uuid
from abc import ABC, abstractmethod

from src.pkm_app.core.application.dtos import (
    UserProfileCreate,
    UserProfileSchema,
    UserProfileUpdate,
)


class IUserProfileRepository(ABC):
    """Interfaz del repositorio de perfiles de usuario."""

    @abstractmethod
    async def get_by_id(self, user_id: str) -> UserProfileSchema | None:
        """Obtiene un perfil de usuario por su ID."""
        raise NotImplementedError

    @abstractmethod
    async def create(self, user_profile_in: UserProfileCreate) -> UserProfileSchema:
        """Crea un nuevo perfil de usuario."""
        raise NotImplementedError

    @abstractmethod
    async def update(
        self, user_id: str, user_profile_in: UserProfileUpdate
    ) -> UserProfileSchema | None:
        """Actualiza un perfil de usuario existente."""
        raise NotImplementedError

    @abstractmethod
    async def delete(self, user_id: str) -> bool:
        """Elimina un perfil de usuario."""
        raise NotImplementedError

    @abstractmethod
    async def list_all(self, skip: int = 0, limit: int = 100) -> list[UserProfileSchema]:
        """Lista todos los perfiles de usuario."""
        raise NotImplementedError
