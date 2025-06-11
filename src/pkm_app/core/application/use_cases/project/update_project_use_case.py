import logging
import uuid

from src.pkm_app.core.application.dtos import ProjectSchema, ProjectUpdate
from src.pkm_app.core.application.interfaces.project_interface import IProjectRepository
from src.pkm_app.core.application.interfaces.unit_of_work_interface import (
    IUnitOfWork,
)
from src.pkm_app.core.domain.errors import (
    PermissionDeniedError,
    ProjectNotFoundError,
    RepositoryError,
    ValidationError,
)

# Configurar logger para este caso de uso
logger = logging.getLogger(__name__)


class UpdateProjectUseCase:
    def __init__(self, project_repository: IProjectRepository, unit_of_work: IUnitOfWork):
        """
        Inicializa el caso de uso de actualización de proyecto.

        Args:
            project_repository: Repositorio de proyectos (IProjectRepository).
            unit_of_work: Unidad de trabajo para transacciones.
        """
        self.project_repository = project_repository
        self.unit_of_work = unit_of_work
        logger.info(
            "UpdateProjectUseCase inicializado con repositorio: %s y unit_of_work: %s",
            project_repository.__class__.__name__,
            unit_of_work.__class__.__name__,
        )

    async def execute(
        self, project_id: uuid.UUID, project_in: ProjectUpdate, user_id: str
    ) -> ProjectSchema:
        """
        Actualiza un proyecto existente.

        Args:
            project_id: ID del proyecto a actualizar.
            project_in: Datos para actualizar el proyecto.
            user_id: ID del usuario que actualiza el proyecto.

        Returns:
            El proyecto actualizado.

        Raises:
            ProjectNotFoundError: Si el proyecto no se encuentra o no pertenece al usuario.
            ValidationError: Si los datos de entrada son inválidos.
            PermissionDeniedError: Si no se proporciona el user_id.
            RepositoryError: Si ocurre un error en la capa de persistencia.
        """
        logger.info(
            "Operación iniciada: Actualizar proyecto",
            extra={
                "user_id": user_id,
                "project_id": str(project_id),
                "operation": "update_project",
            },
        )

        logger.info(
            "Ejecutando UpdateProjectUseCase para user_id=%s, project_id=%s",
            user_id,
            project_id,
        )
        if not user_id:
            logger.warning(
                "Intento de actualización de proyecto sin user_id.",
                extra={"project_id": str(project_id), "operation": "update_project"},
            )
            raise PermissionDeniedError(
                "Se requiere ID de usuario para actualizar un proyecto.",
                context={"operation": "update_project"},
            )
        if not project_id:
            logger.warning(
                "Intento de actualización de proyecto sin project_id.",
                extra={"user_id": user_id, "operation": "update_project"},
            )
            raise ProjectNotFoundError(
                "Se requiere ID de proyecto para actualizar.",
                context={"operation": "update_project"},
            )

        async with self.unit_of_work as uow:
            try:
                project = await uow.projects.get_by_id(project_id, user_id)
                if not project:
                    logger.warning(
                        "Proyecto no encontrado para actualización: %s, user_id=%s",
                        project_id,
                        user_id,
                    )
                    raise ProjectNotFoundError(
                        f"Proyecto {project_id} no encontrado o no pertenece al usuario.",
                        context={"operation": "update_project"},
                    )
                updated_project = await uow.projects.update(project_id, project_in, user_id)
                if updated_project is None:
                    logger.error(
                        "Error inesperado: el método update devolvió None para project_id=%s",
                        project_id,
                    )
                    raise RepositoryError(
                        "El método update del repositorio devolvió None",
                        context={"operation": "update_project"},
                    )
                await uow.commit()
                logger.info("Proyecto actualizado exitosamente: %s", project_id)
                return updated_project
            except Exception as e:
                await uow.rollback()
                logger.error("Error inesperado al actualizar proyecto: %s", e, exc_info=True)
                raise RepositoryError(
                    f"Error al actualizar el proyecto: {e}",
                    context={"operation": "update_project"},
                ) from e
