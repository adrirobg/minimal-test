import logging
import uuid

from src.pkm_app.core.application.dtos import NoteSchema, NoteUpdate
from src.pkm_app.core.application.interfaces.unit_of_work_interface import (
    IUnitOfWork,
)
from src.pkm_app.core.domain.errors import (
    NoteNotFoundError,
    PermissionDeniedError,
    RepositoryError,
    ValidationError,
)

# Configurar logger para este caso de uso
logger = logging.getLogger(__name__)


class UpdateNoteUseCase:
    def __init__(self, unit_of_work: IUnitOfWork):
        self.unit_of_work = unit_of_work

    async def execute(self, note_id: uuid.UUID, note_in: NoteUpdate, user_id: str) -> NoteSchema:
        """
        Actualiza una nota existente.

        Args:
            note_id: ID de la nota a actualizar.
            note_in: Datos para actualizar la nota.
            user_id: ID del usuario que actualiza la nota.

        Returns:
            La nota actualizada.

        Raises:
            NoteNotFoundError: Si la nota no se encuentra o no pertenece al usuario.
            ValidationError: Si los datos de entrada son inválidos o las entidades
                             relacionadas (proyecto, fuente) no existen o no pertenecen al usuario.
            PermissionDeniedError: Si no se proporciona el user_id.
            RepositoryError: Si ocurre un error en la capa de persistencia.
        """
        logger.info(
            "Operación iniciada: Actualizar nota",
            extra={
                "user_id": user_id,
                "note_id": str(note_id),
                "operation": "update_note",
            },
        )

        if not user_id:
            logger.warning(
                "Intento de actualización de nota sin user_id.",
                extra={"note_id": str(note_id), "operation": "update_note"},
            )
            raise PermissionDeniedError(
                "Se requiere ID de usuario para actualizar una nota.",
                context={"operation": "update_note"},
            )
        if not note_id:
            logger.warning(
                "Intento de actualización de nota sin note_id.",
                extra={"user_id": user_id, "operation": "update_note"},
            )
            # Usar ValidationError aquí podría ser más consistente si se considera un input inválido.
            # Sin embargo, NoteNotFoundError también es semánticamente correcto si se interpreta
            # como "no se puede operar sobre una nota no especificada".
            # Por consistencia con el prompt LS1_002 (manejar NoteNotFoundError), lo mantenemos.
            raise NoteNotFoundError(
                "Se requiere ID de nota para actualizarla.",
                context={"operation": "update_note"},
            )

        async with self.unit_of_work as uow:
            try:
                updated_note = await uow.notes.update(
                    note_id=note_id, note_in=note_in, user_id=user_id
                )
                if updated_note is None:
                    raise NoteNotFoundError(
                        "No se encontró la nota a actualizar.",
                        note_id=note_id,
                        context={"operation": "update_note"},
                    )
                await uow.commit()

                logger.info(
                    f"Nota {updated_note.id} actualizada exitosamente",
                    extra={
                        "user_id": user_id,
                        "note_id": str(updated_note.id),
                        "operation": "update_note",
                        "project_id": (
                            str(updated_note.project_id) if updated_note.project_id else None
                        ),
                        "source_id": (
                            str(updated_note.source_id) if updated_note.source_id else None
                        ),
                    },
                )
                return updated_note
            except NoteNotFoundError as e:
                await uow.rollback()
                logger.warning(
                    f"Nota no encontrada al intentar actualizar: {str(e)}",
                    extra={
                        "user_id": user_id,
                        "note_id": str(note_id),
                        "operation": "update_note",
                    },
                )
                # Re-lanzar con contexto de operación
                raise NoteNotFoundError(
                    str(e), note_id=note_id, context={"operation": "update_note"}
                ) from e
            except ValueError as e:  # Errores de validación, ej: project_id inválido
                await uow.rollback()
                logger.warning(
                    f"Error de validación al actualizar nota: {str(e)}",
                    extra={
                        "user_id": user_id,
                        "note_id": str(note_id),
                        "operation": "update_note",
                        "error_message": str(e),
                        "project_id_update": (
                            str(note_in.project_id) if note_in.project_id else None
                        ),
                        "source_id_update": str(note_in.source_id) if note_in.source_id else None,
                    },
                )
                raise ValidationError(str(e), context={"operation": "update_note"}) from e
            except Exception as e:
                await uow.rollback()
                logger.exception(
                    f"Error inesperado al actualizar nota {note_id}: {str(e)}",
                    extra={
                        "user_id": user_id,
                        "note_id": str(note_id),
                        "operation": "update_note",
                    },
                )
                raise RepositoryError(
                    f"Error inesperado en el repositorio al actualizar nota: {str(e)}",
                    operation="update_note",
                    repository_type="NoteRepository",
                    context={"note_id": str(note_id)},
                ) from e
