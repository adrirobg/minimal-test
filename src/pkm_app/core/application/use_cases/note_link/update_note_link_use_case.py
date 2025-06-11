import logging
import uuid

from src.pkm_app.core.application.dtos import NoteLinkSchema, NoteLinkUpdate
from src.pkm_app.core.application.interfaces.unit_of_work_interface import (
    IUnitOfWork,
)
from src.pkm_app.core.domain.errors import (
    NoteLinkNotFoundError,
    PermissionDeniedError,
    RepositoryError,
    ValidationError,
)

# Configurar logger para este caso de uso
logger = logging.getLogger(__name__)


class UpdateNoteLinkUseCase:
    def __init__(self, unit_of_work: IUnitOfWork):
        self.unit_of_work = unit_of_work

    async def execute(
        self, note_link_id: uuid.UUID, note_link_in: NoteLinkUpdate, user_id: str
    ) -> NoteLinkSchema:
        """
        Actualiza un enlace entre notas existente.

        Args:
            note_link_id: ID del enlace a actualizar.
            note_link_in: Datos para actualizar el enlace.
            user_id: ID del usuario que actualiza el enlace.

        Returns:
            El enlace actualizado.

        Raises:
            NoteLinkNotFoundError: Si el enlace no se encuentra o no pertenece al usuario.
            ValidationError: Si los datos de entrada son inválidos o las notas
                             relacionadas no existen o no pertenecen al usuario.
            PermissionDeniedError: Si no se proporciona el user_id.
            RepositoryError: Si ocurre un error en la capa de persistencia.
        """
        logger.info(
            "Operación iniciada: Actualizar enlace entre notas",
            extra={
                "user_id": user_id,
                "note_link_id": str(note_link_id),
                "operation": "update_note_link",
            },
        )

        if not user_id:
            logger.warning(
                "Intento de actualización de enlace sin user_id.",
                extra={"note_link_id": str(note_link_id), "operation": "update_note_link"},
            )
            raise PermissionDeniedError(
                "Se requiere ID de usuario para actualizar un enlace.",
                context={"operation": "update_note_link"},
            )
        if not note_link_id:
            logger.warning(
                "Intento de actualización de enlace sin note_link_id.",
                extra={"user_id": user_id, "operation": "update_note_link"},
            )
            raise NoteLinkNotFoundError(  # Coherente con Get y Delete
                "Se requiere ID de enlace para actualizarlo.",
                note_link_id=note_link_id,  # type: ignore
                context={"operation": "update_note_link"},
            )

        # Validar que al menos un campo se está actualizando
        if not note_link_in.model_fields_set:
            logger.warning(
                "Intento de actualización de enlace sin datos para actualizar.",
                extra={
                    "user_id": user_id,
                    "note_link_id": str(note_link_id),
                    "operation": "update_note_link",
                },
            )
            # Devolver el enlace existente si no hay nada que actualizar, o lanzar error.
            # Por ahora, lanzaremos un error de validación para ser explícitos.
            raise ValidationError(
                "No se proporcionaron datos para actualizar el enlace.",
                context={"operation": "update_note_link"},
            )

        async with self.unit_of_work as uow:
            try:
                # Verificar que el enlace existe y pertenece al usuario antes de validar notas
                existing_link = await uow.note_links.get_by_id(note_link_id, user_id)
                if not existing_link:
                    raise NoteLinkNotFoundError(
                        f"Enlace con ID {note_link_id} no encontrado o no pertenece al usuario.",
                        link_id=note_link_id,
                        context={"operation": "update_note_link"},
                    )

                updated_note_link = await uow.note_links.update(note_link_id, note_link_in, user_id)
                if updated_note_link is None:
                    raise NoteLinkNotFoundError(
                        f"No se encontró el enlace con ID {note_link_id} para actualizar después de la operación.",
                        link_id=note_link_id,
                        context={"operation": "update_note_link"},
                    )
                await uow.commit()

                logger.info(
                    f"Enlace {updated_note_link.id} actualizado exitosamente",
                    extra={
                        "user_id": user_id,
                        "note_link_id": str(updated_note_link.id),
                        "operation": "update_note_link",
                        "updated_data": note_link_in.model_dump(exclude_unset=True),
                    },
                )
                return updated_note_link
            except NoteLinkNotFoundError as e:
                await uow.rollback()
                logger.warning(
                    f"Enlace no encontrado al intentar actualizar: {str(e)}",
                    extra={
                        "user_id": user_id,
                        "note_link_id": str(note_link_id),
                        "operation": "update_note_link",
                    },
                )
                raise NoteLinkNotFoundError(
                    str(e), link_id=note_link_id, context={"operation": "update_note_link"}
                ) from e
            except ValueError as e:  # Errores de validación, ej: IDs inválidos
                await uow.rollback()
                logger.warning(
                    f"Error de validación al actualizar enlace: {str(e)}",
                    extra={
                        "user_id": user_id,
                        "note_link_id": str(note_link_id),
                        "operation": "update_note_link",
                        "error_message": str(e),
                        "update_data": note_link_in.model_dump(exclude_unset=True),
                    },
                )
                raise ValidationError(str(e), context={"operation": "update_note_link"}) from e
            except RepositoryError as e:
                await uow.rollback()
                logger.error(
                    f"Error de repositorio al actualizar enlace: {str(e)}",
                    extra={
                        "user_id": user_id,
                        "note_link_id": str(note_link_id),
                        "operation": "update_note_link",
                        "error_message": str(e),
                    },
                )
                raise
            except Exception as e:
                await uow.rollback()
                logger.exception(
                    f"Error inesperado al actualizar enlace {note_link_id}: {str(e)}",
                    extra={
                        "user_id": user_id,
                        "note_link_id": str(note_link_id),
                        "operation": "update_note_link",
                    },
                )
                raise RepositoryError(
                    f"Error inesperado en el repositorio al actualizar enlace: {str(e)}",
                    operation="update_note_link",
                    repository_type="NoteLinkRepository",
                    context={"note_link_id": str(note_link_id)},
                ) from e
