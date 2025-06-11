import logging
import uuid
from typing import Optional

from src.pkm_app.core.application.dtos import NoteLinkSchema
from src.pkm_app.core.application.interfaces.unit_of_work_interface import (
    IUnitOfWork,
)
from src.pkm_app.core.domain.errors import PermissionDeniedError, RepositoryError, ValidationError

# Configurar logger para este caso de uso
logger = logging.getLogger(__name__)


class ListNoteLinksUseCase:
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
        self,
        user_id: str,
        source_note_id: uuid.UUID | None = None,
        target_note_id: uuid.UUID | None = None,
        skip: int | None = None,
        limit: int | None = None,
    ) -> list[NoteLinkSchema]:
        """
        Lista los enlaces entre notas de un usuario, opcionalmente filtrados por nota origen o destino,
        con paginación estandarizada.

        Args:
            user_id: ID del usuario cuyos enlaces se listarán.
            source_note_id: ID opcional de la nota origen para filtrar los enlaces.
            target_note_id: ID opcional de la nota destino para filtrar los enlaces.
            skip: Número de enlaces a omitir.
            limit: Número máximo de enlaces a devolver.

        Returns:
            Una lista de enlaces entre notas.

        Raises:
            PermissionDeniedError: Si no se proporciona el user_id.
            ValidationError: Si los parámetros de paginación son inválidos (aunque se corrigen)
                             o si se proporcionan source_note_id y target_note_id al mismo tiempo.
            RepositoryError: Si ocurre un error en la capa de persistencia.
        """
        final_skip = skip if skip is not None else self.DEFAULT_SKIP
        final_limit = limit if limit is not None else self.DEFAULT_LIMIT

        final_skip, final_limit = self._validate_pagination(final_skip, final_limit)

        log_extra = {
            "user_id": user_id,
            "source_note_id": str(source_note_id) if source_note_id else None,
            "target_note_id": str(target_note_id) if target_note_id else None,
            "skip": final_skip,
            "limit": final_limit,
            "operation": "list_note_links",
        }
        logger.info("Operación iniciada: Listar enlaces entre notas", extra=log_extra)

        if not user_id:
            logger.warning(
                "Intento de listar enlaces entre notas sin user_id.",
                extra={"operation": "list_note_links"},
            )
            raise PermissionDeniedError(
                "Se requiere ID de usuario para listar enlaces entre notas.",
                context={"operation": "list_note_links"},
            )

        if source_note_id and target_note_id:
            logger.warning(
                "Intento de listar enlaces con source_note_id y target_note_id simultáneamente.",
                extra=log_extra,
            )
            raise ValidationError(
                "No se pueden proporcionar source_note_id y target_note_id al mismo tiempo.",
                context={"operation": "list_note_links"},
            )

        async with self.unit_of_work as uow:
            try:
                if source_note_id:
                    # Validar que la nota origen existe y pertenece al usuario
                    source_note = await uow.notes.get_by_id(source_note_id, user_id)
                    if not source_note:
                        raise ValidationError(
                            f"La nota origen con ID {source_note_id} no existe o no pertenece al usuario.",
                            context={"field": "source_note_id", "operation": "list_note_links"},
                        )
                    note_links = await uow.note_links.get_links_by_source_note(
                        source_note_id, user_id, final_skip, final_limit
                    )
                elif target_note_id:
                    # Validar que la nota destino existe y pertenece al usuario
                    target_note = await uow.notes.get_by_id(target_note_id, user_id)
                    if not target_note:
                        raise ValidationError(
                            f"La nota destino con ID {target_note_id} no existe o no pertenece al usuario.",
                            context={"field": "target_note_id", "operation": "list_note_links"},
                        )
                    note_links = await uow.note_links.get_links_by_target_note(
                        target_note_id, user_id, final_skip, final_limit
                    )
                else:
                    note_links = await uow.note_links.list_by_user(
                        user_id=user_id, skip=final_skip, limit=final_limit
                    )

                logger.info(
                    f"Listados {len(note_links)} enlaces para usuario {user_id}",
                    extra={**log_extra, "count": len(note_links)},
                )
                return note_links
            except ValidationError:  # Para relanzar las de validación de nota
                await uow.rollback()
                raise
            except RepositoryError as e:
                await uow.rollback()
                logger.exception(
                    f"Error de repositorio al listar enlaces para usuario {user_id}: {str(e)}",
                    extra=log_extra,
                )
                raise
            except Exception as e:
                await uow.rollback()
                logger.exception(
                    f"Error inesperado al listar enlaces para usuario {user_id}: {str(e)}",
                    extra=log_extra,
                )
                raise RepositoryError(
                    f"Error inesperado en el repositorio al listar enlaces: {str(e)}",
                    operation="list_note_links",
                    repository_type="NoteLinkRepository",
                    context=log_extra,
                ) from e
