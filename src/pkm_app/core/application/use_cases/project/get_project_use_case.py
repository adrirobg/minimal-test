import logging
import uuid

from src.pkm_app.core.application.dtos import ProjectSchema
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


class GetProjectUseCase:
    """
    Caso de uso para obtener los detalles de un proyecto.
    Sigue el patrón de user_profile: inyección explícita de repositorio y unit_of_work, logging robusto y uso de DTOs.
    """

    def __init__(self, project_repository: IProjectRepository, unit_of_work: IUnitOfWork) -> None:
        """
        Inicializa el caso de uso de obtención de proyecto.

        Args:
            project_repository: Repositorio de proyectos (IProjectRepository).
            unit_of_work: Unidad de trabajo para transacciones.
        """
        self.project_repository = project_repository
        self.unit_of_work = unit_of_work
        logger.info(
            "GetProjectUseCase inicializado con repositorio: %s y unit_of_work: %s",
            project_repository.__class__.__name__,
            unit_of_work.__class__.__name__,
        )

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

        logger.info(
            "Ejecutando GetProjectUseCase para user_id=%s, project_id=%s",
            user_id,
            project_id,
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
                "Se requiere ID de proyecto para obtener un proyecto.",
                context={"operation": "get_project"},
            )

        async with self.unit_of_work as uow:
            try:
                project = await uow.projects.get_by_id(project_id, user_id)
                if not project:
                    logger.warning(
                        "Proyecto no encontrado: %s para user_id=%s",
                        project_id,
                        user_id,
                    )
                    raise ProjectNotFoundError(
                        f"Proyecto {project_id} no encontrado o no pertenece al usuario.",
                        context={"operation": "get_project"},
                    )
                logger.info("Proyecto obtenido exitosamente: %s", project_id)
                await uow.commit()
                return project
            except Exception as e:
                await uow.rollback()
                logger.error("Error inesperado al obtener proyecto: %s", e, exc_info=True)
                raise RepositoryError(
                    f"Error al obtener el proyecto: {e}",
                    context={"operation": "get_project"},
                ) from e
