import logging
import uuid

from src.pkm_app.core.application.interfaces.project_interface import IProjectRepository
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
    def __init__(self, project_repository: IProjectRepository, unit_of_work: IUnitOfWork) -> None:
        """
        Inicializa el caso de uso de eliminación de proyecto.

        Args:
            project_repository: Repositorio de proyectos (IProjectRepository).
            unit_of_work: Unidad de trabajo para transacciones.
        """
        self.project_repository = project_repository
        self.unit_of_work = unit_of_work
        logger.info(
            "DeleteProjectUseCase inicializado con repositorio: %s y unit_of_work: %s",
            project_repository.__class__.__name__,
            unit_of_work.__class__.__name__,
        )

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

        logger.info(
            "Ejecutando DeleteProjectUseCase para user_id=%s, project_id=%s",
            user_id,
            project_id,
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
                "Se requiere ID de proyecto para eliminar.",
                context={"operation": "delete_project"},
            )

        async with self.unit_of_work as uow:
            try:
                deleted = await uow.projects.delete(project_id, user_id)
                if not deleted:
                    logger.warning(
                        "Proyecto no encontrado para eliminación: %s, user_id=%s",
                        project_id,
                        user_id,
                    )
                    raise ProjectNotFoundError(
                        f"Proyecto {project_id} no encontrado o no pertenece al usuario.",
                        context={"operation": "delete_project"},
                    )
                await uow.commit()
                logger.info("Proyecto eliminado exitosamente: %s", project_id)
                return True
            except Exception as e:
                await uow.rollback()
                logger.error("Error inesperado al eliminar proyecto: %s", e, exc_info=True)
                raise RepositoryError(
                    f"Error al eliminar el proyecto: {e}",
                    context={"operation": "delete_project"},
                ) from e
