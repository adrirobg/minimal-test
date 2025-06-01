import logging
import uuid

from src.pkm_app.core.application.dtos import NoteCreate, NoteSchema
from src.pkm_app.core.application.interfaces.unit_of_work_interface import (
    IUnitOfWork,
)
from src.pkm_app.core.domain.errors import PermissionDeniedError, RepositoryError, ValidationError

# Configurar logger para este caso de uso
logger = logging.getLogger(__name__)


class CreateNoteUseCase:
    def __init__(self, unit_of_work: IUnitOfWork):
        self.unit_of_work = unit_of_work

    async def execute(self, note_in: NoteCreate, user_id: str) -> NoteSchema:
        """
        Crea una nueva nota.

        Args:
            note_in: Datos para crear la nota.
            user_id: ID del usuario que crea la nota.

        Returns:
            La nota creada.

        Raises:
            ValidationError: Si los datos de entrada son inválidos o las entidades
                             relacionadas (proyecto, fuente) no existen o no pertenecen al usuario.
            PermissionDeniedError: Si el usuario no tiene permisos (aunque en este caso
                                   la validación de pertenencia se hace en el repositorio).
            RepositoryError: Si ocurre un error en la capa de persistencia.
        """
        logger.info(
            "Operación iniciada: Crear nota",
            extra={"user_id": user_id, "operation": "create_note"},
        )

        if not user_id:
            # Este error debería ser capturado antes o manejado por un decorador de autenticación.
            # No obstante, mantenemos una validación básica aquí.
            logger.warning(
                "Intento de creación de nota sin user_id.",
                extra={"operation": "create_note"},
            )
            raise PermissionDeniedError(
                "Se requiere ID de usuario para crear una nota.",
                context={"operation": "create_note"},
            )

        if not note_in.content:
            logger.warning(
                "Intento de creación de nota con contenido vacío.",
                extra={"user_id": user_id, "operation": "create_note"},
            )
            raise ValidationError(
                "El contenido de la nota no puede estar vacío.",
                context={"field": "content", "operation": "create_note"},
            )

        async with self.unit_of_work as uow:
            try:
                created_note_schema = await uow.notes.create(note_in=note_in, user_id=user_id)
                await uow.commit()

                logger.info(
                    f"Nota creada exitosamente con ID {created_note_schema.id}",
                    extra={
                        "user_id": user_id,
                        "note_id": str(created_note_schema.id),
                        "operation": "create_note",
                        "project_id": (
                            str(created_note_schema.project_id)
                            if created_note_schema.project_id
                            else None
                        ),
                        "source_id": (
                            str(created_note_schema.source_id)
                            if created_note_schema.source_id
                            else None
                        ),
                    },
                )
                return created_note_schema
            except ValueError as e:
                await uow.rollback()
                logger.warning(
                    f"Error de validación al crear nota: {str(e)}",
                    extra={
                        "user_id": user_id,
                        "operation": "create_note",
                        "error_message": str(e),
                        "project_id": str(note_in.project_id) if note_in.project_id else None,
                        "source_id": str(note_in.source_id) if note_in.source_id else None,
                    },
                )
                raise ValidationError(str(e), context={"operation": "create_note"}) from e
            except Exception as e:
                await uow.rollback()
                logger.exception(
                    f"Error inesperado al crear nota: {str(e)}",
                    extra={"user_id": user_id, "operation": "create_note"},
                )
                raise RepositoryError(
                    f"Error inesperado en el repositorio al crear nota: {str(e)}",
                    operation="create_note",
                    repository_type="NoteRepository",
                ) from e
