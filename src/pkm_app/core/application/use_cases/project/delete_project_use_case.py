import logging
import uuid

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


class DeleteProjectUseCase:
    def __init__(self, unit_of_work: IUnitOfWork):
        self.unit_of_work = unit_of_work

    async def execute(self, project_id: uuid.UUID, user_id: str) -> bool:
        """
        Elimina un proyecto.

        Args:
            project_id: ID del proyecto a eliminar.
            user_id: ID del usuario que elimina el proyecto.

        Returns:
            True si el proyecto fue eliminado.

        Raises:
            ProjectNotFoundError: Si el proyecto no se encuentra o no pertenece al usuario.
            PermissionDeniedError: Si no se proporciona el user_id.
            RepositoryError: Si ocurre un error en la capa de persistencia.
        """
        logger.info(
            "Operación iniciada: Eliminar proyecto",
            extra={
                "user_id": user_id,
                "project_id": str(project_id),
                "operation": "delete_project",
            },
        )

        if not user_id:
            logger.warning(
                "Intento de eliminación de proyecto sin user_id.",
                extra={"project_id": str(project_id), "operation": "delete_project"},
            )
            raise PermissionDeniedError(
                "Se requiere ID de usuario para eliminar un proyecto.",
                context={"operation": "delete_project"},
            )
        if not project_id:
            logger.warning(
                "Intento de eliminación de proyecto sin project_id.",
                extra={"user_id": user_id, "operation": "delete_project"},
            )
            raise ProjectNotFoundError(
                "Se requiere ID de proyecto para eliminarlo.",
                project_id=project_id,  # type: ignore
                context={"operation": "delete_project"},
            )

        async with self.unit_of_work as uow:
            try:
                # Asegúrate de que el repositorio de proyectos (`uow.projects`)
                # tenga un método `delete` que acepte `project_id` y `user_id`,
                # y que lance ProjectNotFoundError si el proyecto no existe o no pertenece al usuario.
                await uow.projects.delete(project_id=project_id, user_id=user_id)
                await uow.commit()

                logger.info(
                    f"Proyecto {project_id} eliminado exitosamente",
                    extra={
                        "user_id": user_id,
                        "project_id": str(project_id),
                        "operation": "delete_project",
                    },
                )
                return True
            except ProjectNotFoundError as e:
                await uow.rollback()
                logger.warning(
                    f"Proyecto no encontrado al intentar eliminar: {str(e)}",
                    extra={
                        "user_id": user_id,
                        "project_id": str(project_id),
                        "operation": "delete_project",
                    },
                )
                raise ProjectNotFoundError(
                    str(e), project_id=project_id, context={"operation": "delete_project"}
                ) from e
            except Exception as e:
                await uow.rollback()
                logger.exception(
                    f"Error inesperado al eliminar proyecto {project_id}: {str(e)}",
                    extra={
                        "user_id": user_id,
                        "project_id": str(project_id),
                        "operation": "delete_project",
                    },
                )
                raise RepositoryError(
                    f"Error inesperado en el repositorio al eliminar proyecto: {str(e)}",
                    operation="delete_project",
                    repository_type="ProjectRepository",
                    context={"project_id": str(project_id)},
                ) from e
