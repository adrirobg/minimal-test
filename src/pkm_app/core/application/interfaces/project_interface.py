from abc import ABC, abstractmethod
from uuid import UUID

from src.pkm_app.core.application.dtos.project_dto import (
    ProjectCreate,
    ProjectSchema,
    ProjectUpdate,
)


class IProjectRepository(ABC):
    """
    Interfaz abstracta para el repositorio de proyectos.
    Define el contrato para las operaciones de persistencia de proyectos.
    """

    @abstractmethod
    async def get_by_id(self, project_id: UUID, user_id: str) -> ProjectSchema | None:
        """
        Obtiene un proyecto por su ID y el ID del usuario.
        Devuelve None si el proyecto no se encuentra o no pertenece al usuario.
        """
        raise NotImplementedError

    @abstractmethod
    async def list_by_user(
        self, user_id: str, skip: int = 0, limit: int = 100
    ) -> list[ProjectSchema]:
        """
        Lista todos los proyectos de un usuario específico, con paginación.
        """
        raise NotImplementedError

    @abstractmethod
    async def create(self, project_in: ProjectCreate, user_id: str) -> ProjectSchema:
        """
        Crea un nuevo proyecto para un usuario específico.
        'project_in' es un esquema Pydantic con los datos para el nuevo proyecto.
        """
        raise NotImplementedError

    @abstractmethod
    async def update(
        self, project_id: UUID, project_in: ProjectUpdate, user_id: str
    ) -> ProjectSchema | None:
        """
        Actualiza un proyecto existente perteneciente a un usuario específico.
        'project_in' es un esquema Pydantic con los campos a actualizar.
        Devuelve el proyecto actualizado o None si no se encuentra o no pertenece al usuario.
        """
        raise NotImplementedError

    @abstractmethod
    async def delete(self, project_id: UUID, user_id: str) -> bool:
        """
        Elimina un proyecto por su ID y el ID del usuario.
        Devuelve True si la eliminación fue exitosa, False en caso contrario.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_children(self, project_id: UUID, user_id: str) -> list[ProjectSchema]:
        """
        Obtiene los proyectos hijos de un proyecto específico.
        Devuelve una lista vacía si el proyecto no tiene hijos o no existe.
        """
        raise NotImplementedError

    @abstractmethod
    async def validate_hierarchy(self, project_id: UUID, parent_id: UUID, user_id: str) -> bool:
        """
        Valida que no exista una jerarquía circular al establecer un padre.
        Devuelve True si la jerarquía es válida, False si se detecta circularidad.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_root_projects(
        self, user_id: str, skip: int = 0, limit: int = 100
    ) -> list[ProjectSchema]:
        """
        Obtiene los proyectos raíz (sin padre) de un usuario específico, con paginación.
        Los proyectos raíz son aquellos que no tienen un proyecto padre.
        """
        raise NotImplementedError
