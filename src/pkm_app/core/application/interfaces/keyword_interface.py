import uuid
from abc import ABC, abstractmethod
from typing import Optional

from src.pkm_app.core.application.dtos import KeywordCreate, KeywordSchema, KeywordUpdate


class IKeywordRepository(ABC):
    """Interfaz del repositorio de keywords."""

    @abstractmethod
    async def get_by_id(self, keyword_id: uuid.UUID, user_id: str) -> KeywordSchema | None:
        """Obtiene un keyword por su ID y user_id."""
        raise NotImplementedError

    @abstractmethod
    async def get_by_name(self, name: str, user_id: str) -> KeywordSchema | None:
        """Obtiene un keyword por su nombre y user_id."""
        raise NotImplementedError

    @abstractmethod
    async def list_by_user(
        self, user_id: str, skip: int = 0, limit: int = 100
    ) -> list[KeywordSchema]:
        """Lista los keywords de un usuario específico."""
        raise NotImplementedError

    @abstractmethod
    async def create(self, keyword_in: KeywordCreate, user_id: str) -> KeywordSchema:
        """Crea un nuevo keyword."""
        raise NotImplementedError

    @abstractmethod
    async def update(
        self, keyword_id: uuid.UUID, keyword_in: KeywordUpdate, user_id: str
    ) -> KeywordSchema | None:
        """Actualiza un keyword existente."""
        raise NotImplementedError

    @abstractmethod
    async def delete(self, keyword_id: uuid.UUID, user_id: str) -> bool:
        """Elimina un keyword."""
        raise NotImplementedError
