import logging
import uuid

from src.pkm_app.core.application.dtos import NoteSchema
from src.pkm_app.core.application.interfaces.unit_of_work_interface import (
    IUnitOfWork,
)
from src.pkm_app.core.domain.errors import NoteNotFoundError, PermissionDeniedError, RepositoryError

# Configurar logger para este caso de uso
logger = logging.getLogger(__name__)


class GetNoteUseCase:
    def __init__(self, unit_of_work: IUnitOfWork):
        self.unit_of_work = unit_of_work

    async def execute(self, note_id: uuid.UUID, user_id: str) -> NoteSchema:
        """
        Obtiene los detalles de una nota específica.

        Args:
            note_id: ID de la nota a obtener.
            user_id: ID del usuario que solicita la nota.

        Returns:
            Los detalles de la nota.

        Raises:
            NoteNotFoundError: Si la nota no se encuentra o no pertenece al usuario.
            PermissionDeniedError: Si no se proporciona el user_id.
            RepositoryError: Si ocurre un error en la capa de persistencia.
        """
        logger.info(
            "Operación iniciada: Obtener nota",
            extra={
                "user_id": user_id,
                "note_id": str(note_id),
                "operation": "get_note",
            },
        )

        if not user_id:
            logger.warning(
                "Intento de obtener nota sin user_id.",
                extra={"note_id": str(note_id), "operation": "get_note"},
            )
            raise PermissionDeniedError(
                "Se requiere ID de usuario para obtener una nota.",
                context={"operation": "get_note"},
            )
        if not note_id:
            logger.warning(
                "Intento de obtener nota sin note_id.",
                extra={"user_id": user_id, "operation": "get_note"},
            )
            raise NoteNotFoundError(
                "Se requiere ID de nota para obtenerla.",
                note_id=note_id,  # type: ignore
                context={"operation": "get_note"},
            )

        async with self.unit_of_work as uow:
            try:
                note = await uow.notes.get_by_id(note_id=note_id, user_id=user_id)
                if not note:
                    # Aunque el repositorio podría lanzar NoteNotFoundError,
                    # es más robusto que el caso de uso también lo maneje si el repo devuelve None.
                    logger.warning(
                        f"Nota {note_id} no encontrada por el repositorio para el usuario {user_id}.",
                        extra={
                            "user_id": user_id,
                            "note_id": str(note_id),
                            "operation": "get_note",
                        },
                    )
                    raise NoteNotFoundError(
                        f"Nota con ID {note_id} no encontrada o no pertenece al usuario.",
                        note_id=note_id,
                        context={"operation": "get_note", "user_id": user_id},
                    )

                logger.info(
                    f"Nota {note.id} obtenida exitosamente",
                    extra={
                        "user_id": user_id,
                        "note_id": str(note.id),
                        "operation": "get_note",
                    },
                )
                return note
            except NoteNotFoundError as e:
                await uow.rollback()
                # No es necesario loggear de nuevo si ya se loggeó arriba o si la excepción viene del repo
                # y ya tiene suficiente contexto. Pero si la relanzamos, mantenemos el log.
                logger.warning(
                    f"Nota no encontrada al intentar obtener (relanzando): {str(e)}",
                    extra={
                        "user_id": user_id,
                        "note_id": str(note_id),
                        "operation": "get_note",
                    },
                )
                # Asegurar que el contexto de la operación se mantenga si la excepción viene del repo
                e.context = e.context or {}
                e.context.update({"operation": "get_note"})
                raise
            except Exception as e:
                await uow.rollback()
                logger.exception(
                    f"Error inesperado al obtener nota {note_id}: {str(e)}",
                    extra={
                        "user_id": user_id,
                        "note_id": str(note_id),
                        "operation": "get_note",
                    },
                )
                raise RepositoryError(
                    f"Error inesperado en el repositorio al obtener nota: {str(e)}",
                    operation="get_note",
                    repository_type="NoteRepository",
                    context={"note_id": str(note_id)},
                ) from e
