import logging

from src.pkm_app.core.application.dtos import NoteSchema
from src.pkm_app.core.application.interfaces.unit_of_work_interface import (
    IUnitOfWork,
)
from src.pkm_app.core.domain.errors import PermissionDeniedError, RepositoryError, ValidationError

# Configurar logger para este caso de uso
logger = logging.getLogger(__name__)


class ListNotesUseCase:
    DEFAULT_SKIP = 0
    DEFAULT_LIMIT = 50  # Estandarizado según LS1_005
    MAX_LIMIT = 100  # Estandarizado según LS1_005

    def __init__(self, unit_of_work: IUnitOfWork):
        self.unit_of_work = unit_of_work

    def _validate_pagination(self, skip: int, limit: int) -> tuple[int, int]:
        if skip < 0:
            logger.warning(f"Valor de skip negativo ({skip}) recibido, usando {self.DEFAULT_SKIP}.")
            skip = self.DEFAULT_SKIP
        if limit < 0:  # Aunque el prompt no lo pide, es buena práctica validarlo
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
    ) -> list[NoteSchema]:
        """
        Lista las notas de un usuario con paginación estandarizada.

        Args:
            user_id: ID del usuario cuyas notas se listarán.
            skip: Número de notas a omitir.
            limit: Número máximo de notas a devolver.

        Returns:
            Una lista de notas.

        Raises:
            PermissionDeniedError: Si no se proporciona el user_id.
            ValidationError: Si los parámetros de paginación son inválidos (aunque se corrigen).
            RepositoryError: Si ocurre un error en la capa de persistencia.
        """
        final_skip = skip if skip is not None else self.DEFAULT_SKIP
        final_limit = limit if limit is not None else self.DEFAULT_LIMIT

        final_skip, final_limit = self._validate_pagination(final_skip, final_limit)

        logger.info(
            "Operación iniciada: Listar notas",
            extra={
                "user_id": user_id,
                "skip": final_skip,
                "limit": final_limit,
                "operation": "list_notes",
            },
        )

        if not user_id:
            logger.warning(
                "Intento de listar notas sin user_id.",
                extra={"operation": "list_notes"},
            )
            raise PermissionDeniedError(
                "Se requiere ID de usuario para listar notas.",
                context={"operation": "list_notes"},
            )

        async with self.unit_of_work as uow:
            try:
                notes = await uow.notes.list_by_user(
                    user_id=user_id, skip=final_skip, limit=final_limit
                )

                logger.info(
                    f"Listadas {len(notes)} notas para usuario {user_id}",
                    extra={
                        "user_id": user_id,
                        "count": len(notes),
                        "skip": final_skip,
                        "limit": final_limit,
                        "operation": "list_notes",
                    },
                )
                return notes
            except Exception as e:
                await uow.rollback()  # Asegurar rollback en caso de excepción inesperada
                logger.exception(
                    f"Error inesperado al listar notas para usuario {user_id}: {str(e)}",
                    extra={
                        "user_id": user_id,
                        "skip": final_skip,
                        "limit": final_limit,
                        "operation": "list_notes",
                    },
                )
                raise RepositoryError(
                    f"Error inesperado en el repositorio al listar notas: {str(e)}",
                    operation="list_notes",
                    repository_type="NoteRepository",
                    context={"user_id": user_id, "skip": final_skip, "limit": final_limit},
                ) from e
