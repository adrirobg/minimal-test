import logging
import uuid

from src.pkm_app.core.application.dtos import ProjectSchema
from src.pkm_app.core.application.interfaces.unit_of_work_interface import (
    IUnitOfWork,
)
from src.pkm_app.core.domain.errors import (
    PermissionDeniedError,
    ProjectNotFoundError,
    RepositoryError,
)

# Configurar logger para este caso de uso
logger = logging.getLogger(__name__)


class GetProjectUseCase:
    def __init__(self, unit_of_work: IUnitOfWork):
        self.unit_of_work = unit_of_work

    async def execute(self, project_id: uuid.UUID, user_id: str) -> ProjectSchema:
        """
        Obtiene los detalles de un proyecto específico.

        Args:
            project_id: ID del proyecto a obtener.
            user_id: ID del usuario que solicita el proyecto.

        Returns:
            Los detalles del proyecto.

        Raises:
            ProjectNotFoundError: Si el proyecto no se encuentra o no pertenece al usuario.
            PermissionDeniedError: Si no se proporciona el user_id.
            RepositoryError: Si ocurre un error en la capa de persistencia.
        """
        logger.info(
            "Operación iniciada: Obtener proyecto",
            extra={
                "user_id": user_id,
                "project_id": str(project_id),
                "operation": "get_project",
            },
        )

        if not user_id:
            logger.warning(
                "Intento de obtener proyecto sin user_id.",
                extra={"project_id": str(project_id), "operation": "get_project"},
            )
            raise PermissionDeniedError(
                "Se requiere ID de usuario para obtener un proyecto.",
                context={"operation": "get_project"},
            )
        if not project_id:
            logger.warning(
                "Intento de obtener proyecto sin project_id.",
                extra={"user_id": user_id, "operation": "get_project"},
            )
            raise ProjectNotFoundError(
                "Se requiere ID de proyecto para obtenerlo.",
                project_id=project_id,  # type: ignore
                context={"operation": "get_project"},
            )

        async with self.unit_of_work as uow:
            try:
                # Asegúrate de que el repositorio de proyectos (`uow.projects`)
                # tenga un método `get_by_id` que acepte `project_id` y `user_id`.
                project = await uow.projects.get_by_id(project_id=project_id, user_id=user_id)
                if not project:
                    logger.warning(
                        f"Proyecto {project_id} no encontrado por el repositorio para el usuario {user_id}.",
                        extra={
                            "user_id": user_id,
                            "project_id": str(project_id),
                            "operation": "get_project",
                        },
                    )
                    raise ProjectNotFoundError(
                        f"Proyecto con ID {project_id} no encontrado o no pertenece al usuario.",
                        project_id=project_id,
                        context={"operation": "get_project", "user_id": user_id},
                    )

                logger.info(
                    f"Proyecto {project.id} obtenido exitosamente",
                    extra={
                        "user_id": user_id,
                        "project_id": str(project.id),
                        "operation": "get_project",
                    },
                )
                return project
            except ProjectNotFoundError as e:
                await uow.rollback()
                logger.warning(
                    f"Proyecto no encontrado al intentar obtener (relanzando): {str(e)}",
                    extra={
                        "user_id": user_id,
                        "project_id": str(project_id),
                        "operation": "get_project",
                    },
                )
                e.context = e.context or {}
                e.context.update({"operation": "get_project"})
                raise
            except Exception as e:
                await uow.rollback()
                logger.exception(
                    f"Error inesperado al obtener proyecto {project_id}: {str(e)}",
                    extra={
                        "user_id": user_id,
                        "project_id": str(project_id),
                        "operation": "get_project",
                    },
                )
                raise RepositoryError(
                    f"Error inesperado en el repositorio al obtener proyecto: {str(e)}",
                    operation="get_project",
                    repository_type="ProjectRepository",
                    context={"project_id": str(project_id)},
                ) from e
