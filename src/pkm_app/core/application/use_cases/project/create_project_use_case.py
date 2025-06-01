import logging
import uuid

from src.pkm_app.core.application.dtos import ProjectCreate, ProjectSchema
from src.pkm_app.core.application.interfaces.unit_of_work_interface import (
    IUnitOfWork,
)
from src.pkm_app.core.domain.errors import PermissionDeniedError, RepositoryError, ValidationError

# Configurar logger para este caso de uso
logger = logging.getLogger(__name__)


class CreateProjectUseCase:
    def __init__(self, unit_of_work: IUnitOfWork):
        self.unit_of_work = unit_of_work

    async def execute(self, project_in: ProjectCreate, user_id: str) -> ProjectSchema:
        """
        Crea un nuevo proyecto.

        Args:
            project_in: Datos para crear el proyecto.
            user_id: ID del usuario que crea el proyecto.

        Returns:
            El proyecto creado.

        Raises:
            ValidationError: Si los datos de entrada son inválidos.
            PermissionDeniedError: Si el usuario no tiene permisos.
            RepositoryError: Si ocurre un error en la capa de persistencia.
        """
        logger.info(
            "Operación iniciada: Crear proyecto",
            extra={"user_id": user_id, "operation": "create_project"},
        )

        if not user_id:
            logger.warning(
                "Intento de creación de proyecto sin user_id.",
                extra={"operation": "create_project"},
            )
            raise PermissionDeniedError(
                "Se requiere ID de usuario para crear un proyecto.",
                context={"operation": "create_project"},
            )

        if not project_in.name:
            logger.warning(
                "Intento de creación de proyecto con nombre vacío.",
                extra={"user_id": user_id, "operation": "create_project"},
            )
            raise ValidationError(
                "El nombre del proyecto no puede estar vacío.",
                context={"field": "name", "operation": "create_project"},
            )

        async with self.unit_of_work as uow:
            try:
                # Asegúrate de que el repositorio de proyectos (`uow.projects`)
                # tenga un método `create` que acepte `project_in` y `user_id`.
                created_project_schema = await uow.projects.create(
                    project_in=project_in, user_id=user_id
                )
                await uow.commit()

                logger.info(
                    f"Proyecto creado exitosamente con ID {created_project_schema.id}",
                    extra={
                        "user_id": user_id,
                        "project_id": str(created_project_schema.id),
                        "operation": "create_project",
                    },
                )
                return created_project_schema
            except ValueError as e:
                await uow.rollback()
                logger.warning(
                    f"Error de validación al crear proyecto: {str(e)}",
                    extra={
                        "user_id": user_id,
                        "operation": "create_project",
                        "error_message": str(e),
                    },
                )
                raise ValidationError(str(e), context={"operation": "create_project"}) from e
            except Exception as e:
                await uow.rollback()
                logger.exception(
                    f"Error inesperado al crear proyecto: {str(e)}",
                    extra={"user_id": user_id, "operation": "create_project"},
                )
                raise RepositoryError(
                    f"Error inesperado en el repositorio al crear proyecto: {str(e)}",
                    operation="create_project",
                    repository_type="ProjectRepository",
                ) from e
