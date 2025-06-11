from abc import ABC, abstractmethod
from uuid import UUID

from src.pkm_app.core.application.dtos.source_dto import SourceCreate, SourceSchema, SourceUpdate


class ISourceRepository(ABC):
    """
    Interfaz abstracta para el repositorio de fuentes.
    Define el contrato para las operaciones de persistencia de fuentes.
    """

    @abstractmethod
    async def get_by_id(self, source_id: UUID, user_id: str) -> SourceSchema | None:
        """
        Obtiene una fuente por su ID y el ID del usuario.
        Devuelve None si la fuente no se encuentra o no pertenece al usuario.
        """
        raise NotImplementedError

    @abstractmethod
    async def list_by_user(
        self, user_id: str, skip: int = 0, limit: int = 100
    ) -> list[SourceSchema]:
        """
        Lista todas las fuentes de un usuario específico, con paginación.
        """
        raise NotImplementedError

    @abstractmethod
    async def create(self, source_in: SourceCreate, user_id: str) -> SourceSchema:
        """
        Crea una nueva fuente para un usuario específico.
        'source_in' es un esquema Pydantic con los datos para la nueva fuente.
        """
        raise NotImplementedError

    @abstractmethod
    async def update(
        self, source_id: UUID, source_in: SourceUpdate, user_id: str
    ) -> SourceSchema | None:
        """
        Actualiza una fuente existente perteneciente a un usuario específico.
        'source_in' es un esquema Pydantic con los campos a actualizar.
        Devuelve la fuente actualizada o None si no se encuentra o no pertenece al usuario.
        """
        raise NotImplementedError

    @abstractmethod
    async def delete(self, source_id: UUID, user_id: str) -> bool:
        """
        Elimina una fuente por su ID y el ID del usuario.
        Devuelve True si la eliminación fue exitosa, False en caso contrario.
        """
        raise NotImplementedError

    @abstractmethod
    async def search_by_type(
        self, type: str, user_id: str, skip: int = 0, limit: int = 20
    ) -> list[SourceSchema]:
        """
        Busca fuentes por tipo para un usuario específico, con paginación.
        Retorna una lista de fuentes que coinciden con el tipo especificado.
        """
        raise NotImplementedError

    @abstractmethod
    async def search_by_url(self, url: str, user_id: str) -> SourceSchema | None:
        """
        Busca una fuente por URL para un usuario específico.
        Devuelve None si no se encuentra ninguna fuente con la URL especificada.
        """
        raise NotImplementedError

    @abstractmethod
    async def search_by_title(
        self, query: str, user_id: str, skip: int = 0, limit: int = 20
    ) -> list[SourceSchema]:
        """
        Busca fuentes por título para un usuario específico, con paginación.
        Retorna una lista de fuentes cuyo título coincide parcialmente con la consulta.
        """
        raise NotImplementedError
