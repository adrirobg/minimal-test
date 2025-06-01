import logging

from src.pkm_app.core.application.dtos import ProjectSchema
from src.pkm_app.core.application.interfaces.project_interface import IProjectRepository
from src.pkm_app.core.application.interfaces.unit_of_work_interface import (
    IUnitOfWork,
)

# from src.pkm_app.core.application.interfaces import IProjectRepository
from src.pkm_app.core.domain.errors import PermissionDeniedError, RepositoryError, ValidationError

# Configurar logger para este caso de uso
logger = logging.getLogger(__name__)


class ListProjectsUseCase:
    DEFAULT_SKIP = 0
    DEFAULT_LIMIT = 50
    MAX_LIMIT = 100

    def __init__(self, project_repository: IProjectRepository, unit_of_work: IUnitOfWork) -> None:
        """
        Inicializa el caso de uso de listado de proyectos.

        Args:
            project_repository: Repositorio de proyectos (IProjectRepository).
            unit_of_work: Unidad de trabajo para transacciones.
        """
        self.project_repository = project_repository
        self.unit_of_work = unit_of_work
        logger.info(
            "ListProjectsUseCase inicializado con repositorio: %s y unit_of_work: %s",
            project_repository.__class__.__name__,
            unit_of_work.__class__.__name__,
        )

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
        self, user_id: str, skip: int | None = None, limit: int | None = None
    ) -> list[ProjectSchema]:
        """
        Lista los proyectos de un usuario con paginación estandarizada.

        Args:
            user_id: ID del usuario cuyos proyectos se listarán.
            skip: Número de proyectos a omitir.
            limit: Número máximo de proyectos a devolver.

        Returns:
            Una lista de proyectos.

        Raises:
            PermissionDeniedError: Si no se proporciona el user_id.
            ValidationError: Si los parámetros de paginación son inválidos (aunque se corrigen).
            RepositoryError: Si ocurre un error en la capa de persistencia.
        """
        final_skip = skip if skip is not None else self.DEFAULT_SKIP
        final_limit = limit if limit is not None else self.DEFAULT_LIMIT

        final_skip, final_limit = self._validate_pagination(final_skip, final_limit)

        logger.info(
            "Ejecutando ListProjectsUseCase para user_id=%s, skip=%d, limit=%d",
            user_id,
            final_skip,
            final_limit,
        )
        if not user_id:
            logger.warning(
                "Intento de listar proyectos sin user_id.",
                extra={"operation": "list_projects"},
            )
            raise PermissionDeniedError(
                "Se requiere ID de usuario para listar proyectos.",
                context={"operation": "list_projects"},
            )

        async with self.unit_of_work as uow:
            try:
                projects = await uow.projects.list_by_user(
                    user_id=user_id, skip=final_skip, limit=final_limit
                )

                logger.info(
                    f"Listados {len(projects)} proyectos para usuario {user_id}",
                    extra={
                        "user_id": user_id,
                        "count": len(projects),
                        "skip": final_skip,
                        "limit": final_limit,
                        "operation": "list_projects",
                    },
                )
                return projects
            except Exception as e:
                await uow.rollback()
                logger.exception(
                    f"Error inesperado al listar proyectos para usuario {user_id}: {str(e)}",
                    extra={
                        "user_id": user_id,
                        "skip": final_skip,
                        "limit": final_limit,
                        "operation": "list_projects",
                    },
                )
                raise RepositoryError(
                    f"Error inesperado en el repositorio al listar proyectos: {str(e)}",
                    operation="list_projects",
                    repository_type="ProjectRepository",
                    context={"user_id": user_id, "skip": final_skip, "limit": final_limit},
                ) from e
