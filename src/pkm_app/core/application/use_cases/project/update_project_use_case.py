import logging
import uuid

from src.pkm_app.core.application.dtos import ProjectSchema, ProjectUpdate
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
    def __init__(self, unit_of_work: IUnitOfWork):
        self.unit_of_work = unit_of_work

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
                "Se requiere ID de proyecto para actualizarlo.",
                context={"operation": "update_project"},
            )

        if project_in.name is not None and not project_in.name.strip():
            logger.warning(
                "Intento de actualizar proyecto con nombre vacío.",
                extra={
                    "user_id": user_id,
                    "project_id": str(project_id),
                    "operation": "update_project",
                },
            )
            raise ValidationError(
                "El nombre del proyecto no puede estar vacío.",
                context={"field": "name", "operation": "update_project"},
            )

        async with self.unit_of_work as uow:
            try:
                # Asegúrate de que el repositorio de proyectos (`uow.projects`)
                # tenga un método `update` que acepte `project_id`, `project_in` y `user_id`.
                updated_project = await uow.projects.update(
                    project_id=project_id, project_in=project_in, user_id=user_id
                )
                if updated_project is None:  # pragma: no cover
                    # Esta comprobación es una salvaguarda, el repositorio debería lanzar ProjectNotFoundError
                    raise ProjectNotFoundError(
                        "No se encontró el proyecto a actualizar.",
                        project_id=project_id,
                        context={"operation": "update_project"},
                    )
                await uow.commit()

                logger.info(
                    f"Proyecto {updated_project.id} actualizado exitosamente",
                    extra={
                        "user_id": user_id,
                        "project_id": str(updated_project.id),
                        "operation": "update_project",
                    },
                )
                return updated_project
            except ProjectNotFoundError as e:
                await uow.rollback()
                logger.warning(
                    f"Proyecto no encontrado al intentar actualizar: {str(e)}",
                    extra={
                        "user_id": user_id,
                        "project_id": str(project_id),
                        "operation": "update_project",
                    },
                )
                raise ProjectNotFoundError(
                    str(e), project_id=project_id, context={"operation": "update_project"}
                ) from e
            except ValueError as e:  # Errores de validación del repositorio
                await uow.rollback()
                logger.warning(
                    f"Error de validación al actualizar proyecto: {str(e)}",
                    extra={
                        "user_id": user_id,
                        "project_id": str(project_id),
                        "operation": "update_project",
                        "error_message": str(e),
                    },
                )
                raise ValidationError(str(e), context={"operation": "update_project"}) from e
            except Exception as e:
                await uow.rollback()
                logger.exception(
                    f"Error inesperado al actualizar proyecto {project_id}: {str(e)}",
                    extra={
                        "user_id": user_id,
                        "project_id": str(project_id),
                        "operation": "update_project",
                    },
                )
                raise RepositoryError(
                    f"Error inesperado en el repositorio al actualizar proyecto: {str(e)}",
                    operation="update_project",
                    repository_type="ProjectRepository",
                    context={"project_id": str(project_id)},
                ) from e
