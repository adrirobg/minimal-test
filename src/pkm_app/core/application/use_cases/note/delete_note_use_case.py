import logging
import uuid

from src.pkm_app.core.application.interfaces.unit_of_work_interface import (
    IUnitOfWork,
)
from src.pkm_app.core.domain.errors import NoteNotFoundError, PermissionDeniedError, RepositoryError

# Configurar logger para este caso de uso
logger = logging.getLogger(__name__)


class DeleteNoteUseCase:
    def __init__(self, unit_of_work: IUnitOfWork):
        self.unit_of_work = unit_of_work

    async def execute(self, note_id: uuid.UUID, user_id: str) -> bool:
        """
        Elimina una nota.

        Args:
            note_id: ID de la nota a eliminar.
            user_id: ID del usuario que elimina la nota.

        Returns:
            True si la nota fue eliminada, False en caso contrario.

        Raises:
            NoteNotFoundError: Si la nota no se encuentra o no pertenece al usuario.
            PermissionDeniedError: Si no se proporciona el user_id.
            RepositoryError: Si ocurre un error en la capa de persistencia.
        """
        logger.info(
            "Operación iniciada: Eliminar nota",
            extra={
                "user_id": user_id,
                "note_id": str(note_id),
                "operation": "delete_note",
            },
        )

        if not user_id:
            logger.warning(
                "Intento de eliminación de nota sin user_id.",
                extra={"note_id": str(note_id), "operation": "delete_note"},
            )
            raise PermissionDeniedError(
                "Se requiere ID de usuario para eliminar una nota.",
                context={"operation": "delete_note"},
            )
        if not note_id:
            logger.warning(
                "Intento de eliminación de nota sin note_id.",
                extra={"user_id": user_id, "operation": "delete_note"},
            )
            raise NoteNotFoundError(
                "Se requiere ID de nota para eliminarla.",
                note_id=note_id,  # type: ignore
                context={"operation": "delete_note"},
            )

        async with self.unit_of_work as uow:
            try:
                # El método delete del repositorio debería lanzar NoteNotFoundError
                # si la nota no existe o no pertenece al usuario.
                # O devolver True/False y manejarlo aquí. El prompt LS1_003 sugiere
                # "Manejar apropiadamente el caso de nota no encontrada",
                # lo que implica que el caso de uso debe ser consciente de ello.
                # Si uow.notes.delete lanza la excepción, el bloque `if not deleted` no es necesario.
                # Asumiremos que el repositorio lanza NoteNotFoundError según el contrato implícito
                # de los tests y otros casos de uso.
                await uow.notes.delete(note_id=note_id, user_id=user_id)
                await uow.commit()

                logger.info(
                    f"Nota {note_id} eliminada exitosamente",
                    extra={
                        "user_id": user_id,
                        "note_id": str(note_id),
                        "operation": "delete_note",
                    },
                )
                return True
            except NoteNotFoundError as e:
                await uow.rollback()
                logger.warning(
                    f"Nota no encontrada al intentar eliminar: {str(e)}",
                    extra={
                        "user_id": user_id,
                        "note_id": str(note_id),
                        "operation": "delete_note",
                    },
                )
                raise NoteNotFoundError(
                    str(e), note_id=note_id, context={"operation": "delete_note"}
                ) from e
            except Exception as e:
                await uow.rollback()
                logger.exception(
                    f"Error inesperado al eliminar nota {note_id}: {str(e)}",
                    extra={
                        "user_id": user_id,
                        "note_id": str(note_id),
                        "operation": "delete_note",
                    },
                )
                raise RepositoryError(
                    f"Error inesperado en el repositorio al eliminar nota: {str(e)}",
                    operation="delete_note",
                    repository_type="NoteRepository",
                    context={"note_id": str(note_id)},
                ) from e
