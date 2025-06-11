import logging
import uuid

from src.pkm_app.core.application.dtos import NoteSchema, ProjectSchema
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


class SearchNotesByProjectUseCase:
    DEFAULT_SKIP = 0
    DEFAULT_LIMIT = 50  # Estandarizado según LS1_005
    MAX_LIMIT = 100  # Estandarizado según LS1_005
    DEFAULT_ORDER_BY = "created_at"  # Según LS1_006

    def __init__(self, unit_of_work: IUnitOfWork):
        self.unit_of_work = unit_of_work

    def _validate_pagination(self, skip: int, limit: int) -> tuple[int, int]:
        if skip < 0:
            logger.warning(f"Valor de skip negativo ({skip}) recibido, usando {self.DEFAULT_SKIP}.")
            skip = self.DEFAULT_SKIP
        if limit < 0:
            logger.warning(
                f"Valor de limit negativo ({limit}) recibido, usando {self.DEFAULT_LIMIT}."
            )
            limit = self.DEFAULT_LIMIT
        elif limit > self.MAX_LIMIT:
            logger.warning(
                f"Valor de limit ({limit}) excede MAX_LIMIT ({self.MAX_LIMIT}), usando {self.MAX_LIMIT}."
            )
            limit = self.MAX_LIMIT
        return skip, limit

    async def execute(
        self,
        project_id: uuid.UUID,
        user_id: str,
        skip: int | None = None,
        limit: int | None = None,
        order_by: str | None = None,
    ) -> tuple[ProjectSchema, list[NoteSchema]]:
        """
        Busca notas asociadas a un proyecto específico, devolviendo el proyecto y las notas.

        Args:
            project_id: ID del proyecto por el cual buscar notas.
            user_id: ID del usuario que realiza la búsqueda.
            skip: Número de notas a omitir.
            limit: Número máximo de notas a devolver.
            order_by: Campo por el cual ordenar las notas.

        Returns:
            Una tupla conteniendo el esquema del proyecto y una lista de notas asociadas.

        Raises:
            PermissionDeniedError: Si no se proporciona el user_id.
            ProjectNotFoundError: Si el proyecto no existe o no pertenece al usuario.
            ValidationError: Si el project_id no es válido.
            RepositoryError: Si ocurre un error en la capa de persistencia.
        """
        final_skip = skip if skip is not None else self.DEFAULT_SKIP
        final_limit = limit if limit is not None else self.DEFAULT_LIMIT
        final_order_by = order_by if order_by is not None else self.DEFAULT_ORDER_BY

        final_skip, final_limit = self._validate_pagination(final_skip, final_limit)

        logger.info(
            "Operación iniciada: Buscar notas por proyecto",
            extra={
                "user_id": user_id,
                "project_id": str(project_id),
                "skip": final_skip,
                "limit": final_limit,
                "order_by": final_order_by,
                "operation": "search_notes_by_project",
            },
        )

        if not user_id:
            logger.warning(
                "Intento de búsqueda de notas por proyecto sin user_id.",
                extra={
                    "project_id": str(project_id),
                    "operation": "search_notes_by_project",
                },
            )
            raise PermissionDeniedError(
                "Se requiere ID de usuario para buscar notas por proyecto.",
                context={"operation": "search_notes_by_project"},
            )
        if not project_id:
            logger.warning(
                "Intento de búsqueda de notas por proyecto sin project_id.",
                extra={"user_id": user_id, "operation": "search_notes_by_project"},
            )
            raise ValidationError(
                "Se requiere ID de proyecto para la búsqueda.",
                context={"field": "project_id", "operation": "search_notes_by_project"},
            )

        async with self.unit_of_work as uow:
            try:
                project = await uow.projects.get_by_id(project_id=project_id, user_id=user_id)
                if not project:
                    logger.warning(
                        f"Proyecto {project_id} no encontrado para el usuario {user_id}.",
                        extra={
                            "user_id": user_id,
                            "project_id": str(project_id),
                            "operation": "search_notes_by_project",
                        },
                    )
                    raise ProjectNotFoundError(
                        f"Proyecto con ID {project_id} no encontrado o no pertenece al usuario.",
                        project_id=project_id,
                        context={"operation": "search_notes_by_project", "user_id": user_id},
                    )

                # TODO: El repositorio debería aceptar order_by
                notes = await uow.notes.search_by_project(
                    project_id=project_id,
                    user_id=user_id,
                    skip=final_skip,
                    limit=final_limit,
                    # order_by=final_order_by  # Descomentar cuando el repo lo soporte
                )

                logger.info(
                    f"Encontradas {len(notes)} notas para proyecto {project_id}",
                    extra={
                        "user_id": user_id,
                        "project_id": str(project_id),
                        "count": len(notes),
                        "skip": final_skip,
                        "limit": final_limit,
                        "operation": "search_notes_by_project",
                    },
                )
                return project, notes
            except ProjectNotFoundError as e:
                # El rollback no es estrictamente necesario para operaciones de solo lectura,
                # pero se mantiene por consistencia con el patrón general.
                await uow.rollback()
                logger.warning(
                    f"Proyecto no encontrado al buscar notas: {str(e)}",
                    extra={
                        "user_id": user_id,
                        "project_id": str(project_id),
                        "operation": "search_notes_by_project",
                    },
                )
                raise ProjectNotFoundError(
                    str(e),
                    project_id=project_id,
                    context={"operation": "search_notes_by_project"},
                ) from e
            except Exception as e:
                await uow.rollback()
                logger.exception(
                    f"Error inesperado al buscar notas por proyecto {project_id}: {str(e)}",
                    extra={
                        "user_id": user_id,
                        "project_id": str(project_id),
                        "operation": "search_notes_by_project",
                    },
                )
                raise RepositoryError(
                    f"Error inesperado en el repositorio al buscar notas por proyecto: {str(e)}",
                    operation="search_notes_by_project",
                    repository_type="NoteRepository",  # o "ProjectRepository" o ambos
                    context={
                        "user_id": user_id,
                        "project_id": str(project_id),
                        "skip": final_skip,
                        "limit": final_limit,
                    },
                ) from e
