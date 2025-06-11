import logging
from collections.abc import Sequence
from typing import Optional
from uuid import UUID

from aiocache import Cache  # Añadido para caché
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.pkm_app.core.application.dtos.project_dto import (
    ProjectCreate,
    ProjectSchema,
    ProjectUpdate,
)
from src.pkm_app.core.application.interfaces.project_interface import IProjectRepository
from src.pkm_app.infrastructure.persistence.sqlalchemy.models import Project as ProjectModel

logger = logging.getLogger(__name__)


class SQLAlchemyProjectRepository(IProjectRepository):
    def __init__(self, session: AsyncSession, cache: Cache):  # Cache inyectada
        self.session = session
        self.cache = cache

    async def _get_project_instance(
        self, project_id: UUID, user_id: str, include_children: bool = False
    ) -> ProjectModel | None:
        """Método helper para obtener una instancia de ProjectModel."""
        logger.debug(
            f"Consultando instancia de proyecto {project_id} para usuario {user_id}, incluir hijos: {include_children}."
        )
        cache_key = f"project_instance:{user_id}:{project_id}:{include_children}"

        cached_project = await self.cache.get(cache_key)
        if cached_project:
            logger.debug(
                f"Instancia de proyecto {project_id} (hijos: {include_children}) encontrada en caché para usuario {user_id}."
            )
            if isinstance(cached_project, ProjectModel):
                return cached_project
            return None

        logger.debug(
            f"Instancia de proyecto {project_id} (hijos: {include_children}) no encontrada en caché, consultando BD para usuario {user_id}."
        )
        stmt = select(ProjectModel).where(
            ProjectModel.id == project_id, ProjectModel.user_id == user_id
        )

        if include_children:
            stmt = stmt.options(selectinload(ProjectModel.child_projects))

        result = await self.session.execute(stmt)
        project_instance = result.scalar_one_or_none()

        if project_instance:
            # Usar pickle serializer implícitamente o especificar uno si es necesario.
            # ProjectModel como objeto SQLAlchemy podría necesitar ser detached o convertido a un DTO simple para caché si hay problemas de sesión.
            # Por ahora, se asume que el objeto ProjectModel puede ser cacheado directamente por aiocache (usando pickle).
            await self.cache.set(cache_key, project_instance, ttl=600)  # Cache por 10 minutos
            logger.debug(
                f"Instancia de proyecto {project_id} (hijos: {include_children}) guardada en caché para usuario {user_id}."
            )

        return project_instance

    async def _get_project_ancestors(self, project_id: UUID, user_id: str) -> set[UUID]:
        """Obtiene todos los ancestros de un proyecto para validación de jerarquía."""
        # Using a Common Table Expression (CTE) to recursively fetch ancestors
        # This helps to avoid N+1 query problem.
        # The SQL query finds the parent of the current project, then the parent of that parent, and so on.
        # It stops when a project has no parent (parent_project_id is NULL).
        # The `text()` construct is used because SQLAlchemy's ORM doesn't directly support recursive CTEs in a simple way for this specific scenario.
        # We select `parent_project_id` from the CTE where `parent_project_id` is not NULL,
        # effectively giving us all unique ancestor IDs.
        stmt = """
        WITH RECURSIVE ancestors AS (
            SELECT id, parent_project_id
            FROM projects
            WHERE id = :project_id AND user_id = :user_id
            UNION ALL
            SELECT p.id, p.parent_project_id
            FROM projects p
            INNER JOIN ancestors a ON p.id = a.parent_project_id
            WHERE p.user_id = :user_id
        )
        SELECT parent_project_id FROM ancestors WHERE parent_project_id IS NOT NULL
        """
        logger.debug(f"Consultando ancestros para proyecto {project_id}, usuario {user_id}.")
        result = await self.session.execute(select(UUID).from_statement(text(stmt)), {"project_id": project_id, "user_id": user_id})  # type: ignore
        ancestor_ids = {row[0] for row in result}
        logger.debug(
            f"Encontrados {len(ancestor_ids)} ancestros para proyecto {project_id}, usuario {user_id}."
        )
        return ancestor_ids

    async def get_by_id(self, project_id: UUID, user_id: str) -> ProjectSchema | None:
        logger.info(f"Consultando proyecto por ID {project_id} para usuario {user_id}.")
        project_instance = await self._get_project_instance(
            project_id, user_id, include_children=True
        )
        if project_instance:
            logger.debug(f"Proyecto {project_id} encontrado para usuario {user_id}.")
            return ProjectSchema.model_validate(project_instance)
        logger.debug(f"Proyecto {project_id} no encontrado para usuario {user_id}.")
        return None

    async def list_by_user(
        self, user_id: str, skip: int = 0, limit: int = 100
    ) -> list[ProjectSchema]:
        logger.info(f"Listando proyectos para usuario {user_id} con skip={skip}, limit={limit}.")
        stmt = (
            select(ProjectModel)
            .where(ProjectModel.user_id == user_id)
            .options(selectinload(ProjectModel.child_projects))
            .order_by(ProjectModel.name)
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        projects = result.scalars().all()
        logger.debug(f"Encontrados {len(projects)} proyectos para usuario {user_id}.")
        return [ProjectSchema.model_validate(project) for project in projects]

    def _validate_project_data(self, project_data: dict) -> None:
        """Valida los datos del proyecto."""
        # Estos valores deben coincidir con las restricciones de la base de datos
        MAX_NAME_LENGTH = 100
        MAX_DESCRIPTION_LENGTH = 500

        name = project_data.get("name", "")
        description = project_data.get("description")

        if not name:  # Asegurar que el nombre no esté vacío
            raise ValueError("El nombre del proyecto no puede estar vacío.")
        if len(name) > MAX_NAME_LENGTH:
            raise ValueError(
                f"El nombre del proyecto excede la longitud máxima de {MAX_NAME_LENGTH} caracteres."
            )
        if description and len(description) > MAX_DESCRIPTION_LENGTH:
            raise ValueError(
                f"La descripción del proyecto excede la longitud máxima de {MAX_DESCRIPTION_LENGTH} caracteres."
            )

    async def create(self, project_in: ProjectCreate, user_id: str) -> ProjectSchema:
        project_data = project_in.model_dump()
        self._validate_project_data(project_data)
        logger.info(f"Intentando crear proyecto para usuario {user_id}: {project_data.get('name')}")

        # Validar jerarquía si se especifica un padre
        if project_in.parent_project_id:
            parent_exists = await self._get_project_instance(project_in.parent_project_id, user_id)
            if not parent_exists:
                logger.warning(
                    f"Intento de crear proyecto con padre inexistente {project_in.parent_project_id} para usuario {user_id}"
                )
                raise ValueError(
                    f"Proyecto padre con id {project_in.parent_project_id} no encontrado"
                )

        project_instance = ProjectModel(**project_data, user_id=user_id)

        try:
            self.session.add(project_instance)
            await self.session.flush()
            await self.session.refresh(project_instance)
            logger.info(
                f"Proyecto {project_instance.id} creado exitosamente para usuario {user_id}."
            )
            return ProjectSchema.model_validate(project_instance)
        except IntegrityError as e:
            await self.session.rollback()
            logger.error(f"Error de integridad al crear proyecto para usuario {user_id}: {str(e)}")
            raise ValueError("Error de integridad al crear el proyecto") from e
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error inesperado al crear proyecto para usuario {user_id}: {str(e)}")
            raise

    async def update(
        self, project_id: UUID, project_in: ProjectUpdate, user_id: str
    ) -> ProjectSchema | None:
        logger.info(f"Intentando actualizar proyecto {project_id} para usuario {user_id}.")

        # Iniciar la transacción y bloquear la fila del proyecto para la actualización.
        # Esto previene condiciones de carrera si múltiples peticiones intentan actualizar el mismo proyecto concurrentemente.
        # `with_for_update=True` añade `FOR UPDATE` a la consulta SQL, bloqueando la fila seleccionada.
        stmt = (
            select(ProjectModel)
            .where(ProjectModel.id == project_id, ProjectModel.user_id == user_id)
            .with_for_update()
        )
        result = await self.session.execute(stmt)
        project_instance = result.scalar_one_or_none()

        if not project_instance:
            logger.warning(
                f"Intento de actualizar proyecto inexistente {project_id} para usuario {user_id}"
            )
            return None

        update_data = project_in.model_dump(exclude_unset=True)
        # Re-validar datos en la actualización si es necesario,
        # especialmente si los campos validados pueden cambiar.
        # Aquí asumimos que _validate_project_data cubre los campos relevantes.
        # Si solo algunos campos son actualizables y tienen validaciones específicas,
        # podría ser necesario un método de validación diferente o ajustar _validate_project_data.
        relevant_update_data_for_validation = {
            k: v for k, v in update_data.items() if k in ["name", "description"]
        }
        if relevant_update_data_for_validation:  # Solo validar si hay datos relevantes que validar
            # Crear un diccionario temporal con los datos actuales del proyecto y sobreescribir con los actualizados
            # para una validación completa, o validar solo los campos que cambian.
            # Por simplicidad, aquí validamos solo los datos que vienen en el update.
            # Una aproximación más robusta podría ser cargar el project_data completo y aplicar updates antes de validar.
            self._validate_project_data(relevant_update_data_for_validation)

        # Validar jerarquía si se está actualizando el padre
        if "parent_project_id" in update_data:
            new_parent_id = update_data["parent_project_id"]
            if new_parent_id:  # Si se está estableciendo un nuevo padre
                parent_exists = await self._get_project_instance(new_parent_id, user_id)
                if not parent_exists:
                    logger.warning(
                        f"Intento de actualizar proyecto {project_id} con padre inexistente {new_parent_id} para usuario {user_id}"
                    )
                    raise ValueError(f"Proyecto padre con id {new_parent_id} no encontrado")

                if not await self.validate_hierarchy(project_id, new_parent_id, user_id):
                    logger.warning(
                        f"Intento de crear jerarquía circular actualizando {project_id} a padre {new_parent_id} para usuario {user_id}"
                    )
                    raise ValueError("La actualización crearía una jerarquía circular")
            # Si parent_project_id es None en update_data, significa que se está quitando el padre (haciéndolo raíz)
            # lo cual es una operación válida y no requiere validación de jerarquía aquí.

        for field, value in update_data.items():
            setattr(project_instance, field, value)

        try:
            await self.session.flush()
            await self.session.refresh(project_instance)
            logger.info(f"Proyecto {project_id} actualizado exitosamente para usuario {user_id}.")

            # Invalidar caché
            cache_key_with_children = f"project_instance:{user_id}:{project_id}:True"
            cache_key_without_children = f"project_instance:{user_id}:{project_id}:False"
            await self.cache.delete(cache_key_with_children)
            await self.cache.delete(cache_key_without_children)
            logger.debug(f"Caché invalidada para proyecto {project_id}, usuario {user_id}.")

            return ProjectSchema.model_validate(project_instance)
        except IntegrityError as e:
            await self.session.rollback()
            logger.error(
                f"Error de integridad al actualizar proyecto {project_id} para usuario {user_id}: {str(e)}"
            )
            raise ValueError("Error de integridad al actualizar el proyecto") from e
        except Exception as e:
            await self.session.rollback()
            logger.error(
                f"Error inesperado al actualizar proyecto {project_id} para usuario {user_id}: {str(e)}"
            )
            raise

    async def delete(self, project_id: UUID, user_id: str) -> bool:
        logger.info(f"Intentando eliminar proyecto {project_id} para usuario {user_id}.")
        project_instance = await self._get_project_instance(
            project_id, user_id, include_children=True
        )  # Esta llamada ya usa la caché
        if not project_instance:
            logger.warning(
                f"Intento de eliminar proyecto inexistente {project_id} para usuario {user_id}"
            )
            return False
        try:
            # Eliminar recursivamente los subproyectos
            # Cada llamada recursiva a delete invalidará su propia caché
            logger.debug(f"Eliminando subproyectos de {project_id} para usuario {user_id}.")
            for child in project_instance.child_projects:
                await self.delete(child.id, user_id)  # type: ignore

            # Las notas asociadas se manejarán automáticamente por la configuración
            # ondelete="SET NULL" en la relación project_id de Note
            await self.session.delete(project_instance)
            await self.session.flush()
            logger.info(f"Proyecto {project_id} eliminado exitosamente para usuario {user_id}.")

            # Invalidar caché para el proyecto eliminado
            cache_key_with_children = f"project_instance:{user_id}:{project_id}:True"
            cache_key_without_children = f"project_instance:{user_id}:{project_id}:False"
            await self.cache.delete(cache_key_with_children)
            await self.cache.delete(cache_key_without_children)
            logger.debug(
                f"Caché invalidada para proyecto eliminado {project_id}, usuario {user_id}."
            )

            return True
        except IntegrityError as e:
            await self.session.rollback()
            logger.error(
                f"Error de integridad al eliminar proyecto {project_id} para usuario {user_id}: {str(e)}"
            )
            raise ValueError("Error de integridad al eliminar el proyecto") from e
        except Exception as e:
            await self.session.rollback()
            logger.error(
                f"Error inesperado al eliminar proyecto {project_id} para usuario {user_id}: {str(e)}"
            )
            raise

    async def get_children(self, project_id: UUID, user_id: str) -> list[ProjectSchema]:
        logger.info(f"Consultando hijos para proyecto {project_id}, usuario {user_id}.")
        project = await self._get_project_instance(project_id, user_id, include_children=True)
        if not project:
            logger.debug(
                f"Proyecto padre {project_id} no encontrado para usuario {user_id} al buscar hijos."
            )
            return []
        children_schemas = [ProjectSchema.model_validate(child) for child in project.child_projects]
        logger.debug(
            f"Encontrados {len(children_schemas)} hijos para proyecto {project_id}, usuario {user_id}."
        )
        return children_schemas

    async def validate_hierarchy(self, project_id: UUID, parent_id: UUID, user_id: str) -> bool:
        """
        Valida que no se cree una jerarquía circular al establecer parent_id como padre de project_id.
        """
        if project_id == parent_id:
            return False

        # Obtener todos los ancestros del padre propuesto
        try:
            ancestors = await self._get_project_ancestors(parent_id, user_id)
        except ValueError:
            # Si ya hay una referencia circular en los ancestros, no permitir más cambios
            return False

        # Si el proyecto actual está en los ancestros del padre propuesto,
        # se crearía una referencia circular
        return project_id not in ancestors

    async def get_root_projects(
        self, user_id: str, skip: int = 0, limit: int = 100
    ) -> list[ProjectSchema]:
        logger.info(
            f"Listando proyectos raíz para usuario {user_id} con skip={skip}, limit={limit}."
        )
        stmt = (
            select(ProjectModel)
            .where(
                ProjectModel.user_id == user_id,
                ProjectModel.parent_project_id == None,  # noqa: E711
            )
            .options(selectinload(ProjectModel.child_projects))
            .order_by(ProjectModel.name)
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        projects = result.scalars().all()
        logger.debug(f"Encontrados {len(projects)} proyectos raíz para usuario {user_id}.")
        return [ProjectSchema.model_validate(project) for project in projects]
