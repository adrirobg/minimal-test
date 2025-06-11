import logging

from src.pkm_app.core.application.dtos import ProjectCreate, ProjectSchema
from src.pkm_app.core.application.interfaces.unit_of_work_interface import (
    IUnitOfWork,
)
from src.pkm_app.core.domain.errors import PermissionDeniedError, RepositoryError, ValidationError

# Configurar logger para este caso de uso
logger = logging.getLogger(__name__)


class CreateProjectUseCase:
    """
    Caso de uso para crear un nuevo proyecto.
    Sigue el patrón de user_profile: inyección explícita de repositorio y unit_of_work, logging robusto y uso de DTOs.
    """

    def __init__(self, unit_of_work: IUnitOfWork) -> None:
        """
        Inicializa el caso de uso de creación de proyecto.

        Args:
            unit_of_work: Unidad de trabajo para transacciones y acceso a repositorios.
        """
        self.unit_of_work = unit_of_work
        logger.info(
            "CreateProjectUseCase inicializado con unit_of_work: %s",
            unit_of_work.__class__.__name__,
        )

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
            extra={"user_id": user_id, "operation": "create_project", "project_name": project_in.name},
        )

        if not user_id:
            logger.warning(
                "Intento de creación de proyecto sin user_id.",
                extra={"operation": "create_project"},
            )
            raise PermissionDeniedError("Se requiere ID de usuario para crear un proyecto")

        if not project_in.name or not project_in.name.strip():
            logger.warning(
                "Intento de creación de proyecto con nombre vacío.",
                extra={"user_id": user_id, "operation": "create_project"},
            )
            raise ValidationError(
                "El nombre del proyecto no puede estar vacío.",
                context={"field": "name", "operation": "create_project"}
            )

        # Validar jerarquía si se especifica un proyecto padre
        if project_in.parent_project_id:
            async with self.unit_of_work as uow:
                try:
                    parent_project = await uow.projects.get_by_id(
                        project_in.parent_project_id, user_id
                    )
                    if not parent_project:
                        logger.warning(
                            f"Proyecto padre {project_in.parent_project_id} no encontrado.",
                            extra={"user_id": user_id, "operation": "create_project"},
                        )
                        raise ValidationError(
                            f"El proyecto padre con ID {project_in.parent_project_id} no existe o no pertenece al usuario.",
                            context={"field": "parent_project_id", "operation": "create_project"}
                        )
                except ValidationError:
                    raise  # Re-raise validation errors
                except Exception as e:
                    logger.error(
                        f"Error validando proyecto padre: {str(e)}",
                        extra={"user_id": user_id, "operation": "create_project"},
                    )
                    raise RepositoryError(
                        f"Error al validar proyecto padre: {str(e)}",
                        operation="create_project",
                        repository_type="ProjectRepository"
                    ) from e

        async with self.unit_of_work as uow:
            try:
                created_project = await uow.projects.create(project_in=project_in, user_id=user_id)
                await uow.commit()

                logger.info(
                    f"Proyecto creado exitosamente con ID {created_project.id}",
                    extra={
                        "user_id": user_id,
                        "project_id": str(created_project.id),
                        "project_name": created_project.name,
                        "operation": "create_project",
                        "parent_project_id": (
                            str(created_project.parent_project_id)
                            if created_project.parent_project_id
                            else None
                        ),
                    },
                )
                return created_project
            except ValueError as e:
                await uow.rollback()
                logger.warning(
                    f"Error de validación al crear proyecto: {str(e)}",
                    extra={
                        "user_id": user_id,
                        "operation": "create_project",
                        "error_message": str(e),
                        "project_name": project_in.name,
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
