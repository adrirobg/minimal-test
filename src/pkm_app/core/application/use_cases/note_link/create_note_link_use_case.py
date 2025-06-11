import logging
import uuid

from src.pkm_app.core.application.dtos import NoteLinkCreate, NoteLinkSchema
from src.pkm_app.core.application.interfaces.unit_of_work_interface import (
    IUnitOfWork,
)
from src.pkm_app.core.domain.errors import PermissionDeniedError, RepositoryError, ValidationError

# Configurar logger para este caso de uso
logger = logging.getLogger(__name__)


class CreateNoteLinkUseCase:
    def __init__(self, unit_of_work: IUnitOfWork):
        self.unit_of_work = unit_of_work

    async def execute(self, note_link_in: NoteLinkCreate, user_id: str) -> NoteLinkSchema:
        """
        Crea un nuevo enlace entre notas.

        Args:
            note_link_in: Datos para crear el enlace entre notas.
            user_id: ID del usuario que crea el enlace.

        Returns:
            El enlace entre notas creado.

        Raises:
            ValidationError: Si los datos de entrada son inválidos o las notas
                             relacionadas no existen o no pertenecen al usuario.
            PermissionDeniedError: Si el usuario no tiene permisos.
            RepositoryError: Si ocurre un error en la capa de persistencia.
        """
        logger.info(
            "Operación iniciada: Crear enlace entre notas",
            extra={"user_id": user_id, "operation": "create_note_link"},
        )

        if not user_id:
            logger.warning(
                "Intento de creación de enlace entre notas sin user_id.",
                extra={"operation": "create_note_link"},
            )
            raise PermissionDeniedError(
                "Se requiere ID de usuario para crear un enlace entre notas.",
                context={"operation": "create_note_link"},
            )

        if not all(
            [note_link_in.source_note_id, note_link_in.target_note_id, note_link_in.link_type]
        ):
            logger.warning(
                "Intento de creación de enlace entre notas con datos incompletos.",
                extra={
                    "user_id": user_id,
                    "operation": "create_note_link",
                    "data": note_link_in.model_dump_json(),
                },
            )
            missing_fields = []
            if not note_link_in.source_note_id:
                missing_fields.append("source_note_id")
            if not note_link_in.target_note_id:
                missing_fields.append("target_note_id")
            if not note_link_in.link_type:
                missing_fields.append("link_type")

            raise ValidationError(
                f"Los campos {', '.join(missing_fields)} son obligatorios para crear un enlace entre notas.",
                context={"fields": missing_fields, "operation": "create_note_link"},
            )

        async with self.unit_of_work as uow:
            try:
                # Validar que las notas origen y destino existen y pertenecen al usuario
                source_note = await uow.notes.get_by_id(note_link_in.source_note_id, user_id)
                if not source_note or source_note.user_id != user_id:
                    raise ValidationError(
                        f"La nota origen con ID {note_link_in.source_note_id} no existe o no pertenece al usuario.",
                        context={"field": "source_note_id", "operation": "create_note_link"},
                    )

                target_note = await uow.notes.get_by_id(note_link_in.target_note_id, user_id)
                if not target_note or target_note.user_id != user_id:
                    raise ValidationError(
                        f"La nota destino con ID {note_link_in.target_note_id} no existe o no pertenece al usuario.",
                        context={"field": "target_note_id", "operation": "create_note_link"},
                    )

                created_note_link_schema = await uow.note_links.create(note_link_in, user_id)
                await uow.commit()

                logger.info(
                    f"Enlace entre notas creado exitosamente con ID {created_note_link_schema.id}",
                    extra={
                        "user_id": user_id,
                        "note_link_id": str(created_note_link_schema.id),
                        "source_note_id": str(created_note_link_schema.source_note_id),
                        "target_note_id": str(created_note_link_schema.target_note_id),
                        "operation": "create_note_link",
                    },
                )
                return created_note_link_schema
            except ValueError as e:
                await uow.rollback()
                logger.warning(
                    f"Error de validación al crear enlace entre notas: {str(e)}",
                    extra={
                        "user_id": user_id,
                        "operation": "create_note_link",
                        "error_message": str(e),
                        "data": note_link_in.model_dump_json(),
                    },
                )
                raise ValidationError(str(e), context={"operation": "create_note_link"}) from e
            except RepositoryError as e:
                await uow.rollback()
                logger.error(
                    f"Error de repositorio al crear enlace entre notas: {str(e)}",
                    extra={
                        "user_id": user_id,
                        "operation": "create_note_link",
                        "error_message": str(e),
                        "data": note_link_in.model_dump_json(),
                    },
                )
                # Re-lanzar RepositoryError tal cual para que sea manejado por capas superiores
                # y no se enmascare como un error genérico.
                raise
            except Exception as e:
                await uow.rollback()
                logger.exception(
                    f"Error inesperado al crear enlace entre notas: {str(e)}",
                    extra={
                        "user_id": user_id,
                        "operation": "create_note_link",
                        "data": note_link_in.model_dump_json(),
                    },
                )
                if isinstance(e, ValidationError):
                    raise
                raise RepositoryError(
                    f"Error inesperado en el repositorio al crear enlace entre notas: {str(e)}",
                    operation="create_note_link",
                    repository_type="NoteLinkRepository",
                ) from e
