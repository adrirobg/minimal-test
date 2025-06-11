from abc import ABC, abstractmethod
from uuid import UUID

from src.pkm_app.core.application.dtos.note_link_dto import (
    NoteLinkCreate,
    NoteLinkSchema,
    NoteLinkUpdate,
)


class INoteLinkRepository(ABC):
    """
    Interfaz abstracta para el repositorio de enlaces entre notas.
    Define el contrato para las operaciones de persistencia de enlaces.
    """

    @abstractmethod
    async def get_by_id(self, link_id: UUID, user_id: str) -> NoteLinkSchema | None:
        """
        Obtiene un enlace por su ID y el ID del usuario.
        Devuelve None si el enlace no se encuentra o no pertenece al usuario.
        """
        raise NotImplementedError

    @abstractmethod
    async def list_by_user(
        self, user_id: str, skip: int = 0, limit: int = 100
    ) -> list[NoteLinkSchema]:
        """
        Lista todos los enlaces de un usuario específico, con paginación.
        """
        raise NotImplementedError

    @abstractmethod
    async def create(self, link_in: NoteLinkCreate, user_id: str) -> NoteLinkSchema:
        """
        Crea un nuevo enlace para un usuario específico.
        'link_in' es un esquema Pydantic con los datos para el nuevo enlace.
        """
        raise NotImplementedError

    @abstractmethod
    async def update(
        self, link_id: UUID, link_in: NoteLinkUpdate, user_id: str
    ) -> NoteLinkSchema | None:
        """
        Actualiza un enlace existente perteneciente a un usuario específico.
        'link_in' es un esquema Pydantic con los campos a actualizar.
        Devuelve el enlace actualizado o None si no se encuentra o no pertenece al usuario.
        """
        raise NotImplementedError

    @abstractmethod
    async def delete(self, link_id: UUID, user_id: str) -> bool:
        """
        Elimina un enlace por su ID y el ID del usuario.
        Devuelve True si la eliminación fue exitosa, False en caso contrario.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_links_by_source_note(
        self, note_id: UUID, user_id: str, skip: int = 0, limit: int = 20
    ) -> list[NoteLinkSchema]:
        """
        Obtiene todos los enlaces donde la nota especificada es el origen, con paginación.
        Retorna una lista de enlaces que tienen la nota dada como origen.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_links_by_target_note(
        self, note_id: UUID, user_id: str, skip: int = 0, limit: int = 20
    ) -> list[NoteLinkSchema]:
        """
        Obtiene todos los enlaces donde la nota especificada es el destino, con paginación.
        Retorna una lista de enlaces que tienen la nota dada como destino.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_links_by_type(
        self, link_type: str, user_id: str, skip: int = 0, limit: int = 20
    ) -> list[NoteLinkSchema]:
        """
        Obtiene todos los enlaces de un tipo específico para un usuario, con paginación.
        Retorna una lista de enlaces que coinciden con el tipo especificado.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_link_between_notes(
        self, source_note_id: UUID, target_note_id: UUID, user_id: str, link_type: str | None = None
    ) -> NoteLinkSchema | None:
        """
        Obtiene el enlace específico entre dos notas, opcionalmente de un tipo específico.
        Devuelve None si no existe un enlace entre las notas especificadas.

        Args:
            source_note_id: ID de la nota origen
            target_note_id: ID de la nota destino
            user_id: ID del usuario
            link_type: Tipo de enlace (opcional)
        """
        raise NotImplementedError
