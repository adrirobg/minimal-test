import logging

from src.pkm_app.core.application.dtos import SourceSchema
from src.pkm_app.core.application.interfaces.unit_of_work_interface import (
    IUnitOfWork,
)
from src.pkm_app.core.domain.errors import PermissionDeniedError, RepositoryError, ValidationError

# Configurar logger para este caso de uso
logger = logging.getLogger(__name__)


class ListSourcesUseCase:
    DEFAULT_SKIP = 0
    DEFAULT_LIMIT = 50
    MAX_LIMIT = 100

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
        self, user_id: str, skip: int | None = None, limit: int | None = None
    ) -> list[SourceSchema]:
        """
        Lista las fuentes de un usuario con paginación estandarizada.

        Args:
            user_id: ID del usuario cuyas fuentes se listarán.
            skip: Número de fuentes a omitir.
            limit: Número máximo de fuentes a devolver.

        Returns:
            Una lista de fuentes.

        Raises:
            PermissionDeniedError: Si no se proporciona el user_id.
            ValidationError: Si los parámetros de paginación son inválidos (aunque se corrigen).
            RepositoryError: Si ocurre un error en la capa de persistencia.
        """
        final_skip = skip if skip is not None else self.DEFAULT_SKIP
        final_limit = limit if limit is not None else self.DEFAULT_LIMIT

        final_skip, final_limit = self._validate_pagination(final_skip, final_limit)

        logger.info(
            "Operación iniciada: Listar fuentes",
            extra={
                "user_id": user_id,
                "skip": final_skip,
                "limit": final_limit,
                "operation": "list_sources",
            },
        )

        if not user_id:
            logger.warning(
                "Intento de listar fuentes sin user_id.",
                extra={"operation": "list_sources"},
            )
            raise PermissionDeniedError(
                "Se requiere ID de usuario para listar fuentes.",
                context={"operation": "list_sources"},
            )

        async with self.unit_of_work as uow:
            try:
                sources = await uow.sources.list_by_user(
                    user_id=user_id, skip=final_skip, limit=final_limit
                )

                logger.info(
                    f"Listadas {len(sources)} fuentes para usuario {user_id}",
                    extra={
                        "user_id": user_id,
                        "count": len(sources),
                        "skip": final_skip,
                        "limit": final_limit,
                        "operation": "list_sources",
                    },
                )
                return sources
            except Exception as e:
                await uow.rollback()
                logger.exception(
                    f"Error inesperado al listar fuentes para usuario {user_id}: {str(e)}",
                    extra={
                        "user_id": user_id,
                        "skip": final_skip,
                        "limit": final_limit,
                        "operation": "list_sources",
                    },
                )
                raise RepositoryError(
                    f"Error inesperado en el repositorio al listar fuentes: {str(e)}",
                    operation="list_sources",
                    repository_type="SourceRepository",
                    context={"user_id": user_id, "skip": final_skip, "limit": final_limit},
                ) from e
