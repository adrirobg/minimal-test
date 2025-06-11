import logging
import uuid

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


class DeleteNoteLinkUseCase:
    def __init__(self, unit_of_work: IUnitOfWork):
        self.unit_of_work = unit_of_work

    async def execute(self, note_link_id: uuid.UUID, user_id: str) -> bool:
        """
        Elimina un enlace entre notas.

        Args:
            note_link_id: ID del enlace a eliminar.
            user_id: ID del usuario que elimina el enlace.

        Returns:
            True si el enlace fue eliminado.

        Raises:
            NoteLinkNotFoundError: Si el enlace no se encuentra o no pertenece al usuario.
            PermissionDeniedError: Si no se proporciona el user_id.
            ValidationError: Si el note_link_id no es válido.
            RepositoryError: Si ocurre un error en la capa de persistencia.
        """
        logger.info(
            "Operación iniciada: Eliminar enlace entre notas",
            extra={
                "user_id": user_id,
                "note_link_id": str(note_link_id),
                "operation": "delete_note_link",
            },
        )

        if not user_id:
            logger.warning(
                "Intento de eliminación de enlace sin user_id.",
                extra={"note_link_id": str(note_link_id), "operation": "delete_note_link"},
            )
            raise PermissionDeniedError(
                "Se requiere ID de usuario para eliminar un enlace.",
                context={"operation": "delete_note_link"},
            )
        if not note_link_id:
            logger.warning(
                "Intento de eliminación de enlace sin note_link_id.",
                extra={"user_id": user_id, "operation": "delete_note_link"},
            )
            # Usamos ValidationError aquí porque un ID nulo no es un "no encontrado" sino una entrada inválida.
            # Aunque en GetNoteLinkUseCase se usa NoteLinkNotFoundError para un ID nulo,
            # aquí es más consistente con la idea de que la operación no puede proceder con un ID inválido.
            # Sin embargo, para mantener consistencia con Get y Update, usaremos NoteLinkNotFoundError.
            raise NoteLinkNotFoundError(
                "Se requiere ID de enlace para eliminarlo.",
                note_link_id=note_link_id,  # type: ignore
                context={"operation": "delete_note_link"},
            )

        async with self.unit_of_work as uow:
            try:
                # El método delete del repositorio debería lanzar NoteLinkNotFoundError
                # si el enlace no existe o no pertenece al usuario.
                await uow.note_links.delete(note_link_id, user_id)
                await uow.commit()

                logger.info(
                    f"Enlace {note_link_id} eliminado exitosamente",
                    extra={
                        "user_id": user_id,
                        "note_link_id": str(note_link_id),
                        "operation": "delete_note_link",
                    },
                )
                return True
            except NoteLinkNotFoundError as e:
                await uow.rollback()
                logger.warning(
                    f"Enlace no encontrado al intentar eliminar: {str(e)}",
                    extra={
                        "user_id": user_id,
                        "note_link_id": str(note_link_id),
                        "operation": "delete_note_link",
                    },
                )
                # Re-lanzar con contexto de operación
                raise NoteLinkNotFoundError(
                    str(e), link_id=note_link_id, context={"operation": "delete_note_link"}
                ) from e
            except RepositoryError as e:
                await uow.rollback()
                logger.error(
                    f"Error de repositorio al eliminar enlace: {str(e)}",
                    extra={
                        "user_id": user_id,
                        "note_link_id": str(note_link_id),
                        "operation": "delete_note_link",
                        "error_message": str(e),
                    },
                )
                raise
            except Exception as e:
                await uow.rollback()
                logger.exception(
                    f"Error inesperado al eliminar enlace {note_link_id}: {str(e)}",
                    extra={
                        "user_id": user_id,
                        "note_link_id": str(note_link_id),
                        "operation": "delete_note_link",
                    },
                )
                raise RepositoryError(
                    f"Error inesperado en el repositorio al eliminar enlace: {str(e)}",
                    operation="delete_note_link",
                    repository_type="NoteLinkRepository",
                    context={"note_link_id": str(note_link_id)},
                ) from e
