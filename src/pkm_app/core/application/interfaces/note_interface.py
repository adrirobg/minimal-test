# src/pkm_app/core/application/interfaces/note_interface.py

import uuid
from abc import ABC, abstractmethod
from typing import Optional

from src.pkm_app.core.application.dtos import (
    NoteCreate,
    NoteSchema,
    NoteUpdate,
)


class INoteRepository(ABC):
    """
    Interfaz abstracta para el repositorio de notas.
    Define el contrato para las operaciones de persistencia de notas.
    """

    @abstractmethod
    async def get_by_id(
        self, note_id: uuid.UUID, user_id: str
    ) -> NoteSchema | None:  # Cambiado de Awaitable[NoteSchema | None]
        """
        Obtiene una nota por su ID y el ID del usuario.
        Devuelve None si la nota no se encuentra o no pertenece al usuario.
        """
        raise NotImplementedError

    @abstractmethod
    async def list_by_user(  # Añadido async
        self, user_id: str, skip: int = 0, limit: int = 100
    ) -> list[NoteSchema]:
        """
        Lista las notas de un usuario específico, con paginación.
        """
        raise NotImplementedError

    @abstractmethod
    async def create(
        self, note_in: NoteCreate, user_id: str
    ) -> NoteSchema:  # Cambiado de Awaitable[NoteSchema]
        """
        Crea una nueva nota para un usuario específico.
        'note_in' es un esquema Pydantic con los datos para la nueva nota.
        Debe manejar la asociación de keywords si 'note_in.keywords' (lista de nombres de keywords) está presente.
        """
        raise NotImplementedError

    @abstractmethod
    async def update(  # Añadido async
        self, note_id: uuid.UUID, note_in: NoteUpdate, user_id: str
    ) -> NoteSchema | None:
        """
        Actualiza una nota existente perteneciente a un usuario específico.
        'note_in' es un esquema Pydantic con los campos a actualizar.
        Devuelve la nota actualizada o None si la nota no se encuentra o no pertenece al usuario.
        Debe manejar la actualización de la asociación de keywords si 'note_in.keywords' está presente.
        """
        raise NotImplementedError

    @abstractmethod
    async def delete(self, note_id: uuid.UUID, user_id: str) -> bool:  # Añadido async
        """
        Elimina una nota por su ID y el ID del usuario.
        Devuelve True si la eliminación fue exitosa, False en caso contrario.
        """
        raise NotImplementedError

    @abstractmethod
    async def search_by_title_or_content(  # Añadido async
        self, user_id: str, query: str, skip: int = 0, limit: int = 20
    ) -> list[NoteSchema]:
        """
        Busca notas por una cadena de consulta en el título o contenido.
        """
        raise NotImplementedError

    # Podríamos añadir más métodos específicos aquí según las necesidades, por ejemplo:
    @abstractmethod
    async def search_by_project(  # Añadido async
        self, project_id: uuid.UUID, user_id: str, skip: int = 0, limit: int = 20
    ) -> list[NoteSchema]:
        """
        Lista las notas asociadas a un proyecto específico.
        """
        raise NotImplementedError

    @abstractmethod
    async def search_by_keyword_name(  # Añadido async
        self,
        keyword_name: str,
        project_id: uuid.UUID | None,
        user_id: str,
        skip: int = 0,
        limit: int = 20,
    ) -> list[NoteSchema]:
        """
        Lista las notas asociadas a una keyword específica en un proyecto.
        """
        raise NotImplementedError

    @abstractmethod
    async def search_by_keyword_names(  # Añadido async
        self,
        keyword_names: list[str],
        project_id: uuid.UUID,
        user_id: str,
        skip: int = 0,
        limit: int = 20,
    ) -> list[NoteSchema]:
        """
        Lista las notas asociadas a una lista de keywords específicas en un proyecto.
        """
        raise NotImplementedError
