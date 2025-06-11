import logging
import uuid

from src.pkm_app.core.application.dtos import NoteLinkSchema
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


class GetNoteLinkUseCase:
    def __init__(self, unit_of_work: IUnitOfWork):
        self.unit_of_work = unit_of_work

    async def execute(self, note_link_id: uuid.UUID, user_id: str) -> NoteLinkSchema:
        """
        Obtiene los detalles de un enlace entre notas específico.

        Args:
            note_link_id: ID del enlace entre notas a obtener.
            user_id: ID del usuario que solicita el enlace.

        Returns:
            Los detalles del enlace entre notas.

        Raises:
            NoteLinkNotFoundError: Si el enlace no se encuentra o no pertenece al usuario.
            PermissionDeniedError: Si no se proporciona el user_id.
            ValidationError: Si el note_link_id no es válido.
            RepositoryError: Si ocurre un error en la capa de persistencia.
        """
        logger.info(
            "Operación iniciada: Obtener enlace entre notas",
            extra={
                "user_id": user_id,
                "note_link_id": str(note_link_id),
                "operation": "get_note_link",
            },
        )

        if not user_id:
            logger.warning(
                "Intento de obtener enlace entre notas sin user_id.",
                extra={"note_link_id": str(note_link_id), "operation": "get_note_link"},
            )
            raise PermissionDeniedError(
                "Se requiere ID de usuario para obtener un enlace entre notas.",
                context={"operation": "get_note_link"},
            )
        if not note_link_id:
            logger.warning(
                "Intento de obtener enlace entre notas sin note_link_id.",
                extra={"user_id": user_id, "operation": "get_note_link"},
            )
            # Usamos ValidationError aquí porque un ID nulo no es un "no encontrado" sino una entrada inválida.
            raise ValidationError(
                "Se requiere ID de enlace para obtenerlo.",
                context={"field": "note_link_id", "operation": "get_note_link"},
            )

        async with self.unit_of_work as uow:
            try:
                note_link = await uow.note_links.get_by_id(note_link_id, user_id)
                if not note_link:
                    logger.warning(
                        f"Enlace {note_link_id} no encontrado por el repositorio para el usuario {user_id}.",
                        extra={
                            "user_id": user_id,
                            "note_link_id": str(note_link_id),
                            "operation": "get_note_link",
                        },
                    )
                    raise NoteLinkNotFoundError(
                        f"Enlace con ID {note_link_id} no encontrado o no pertenece al usuario.",
                        link_id=note_link_id,
                        context={"operation": "get_note_link", "user_id": user_id},
                    )

                logger.info(
                    f"Enlace {note_link.id} obtenido exitosamente",
                    extra={
                        "user_id": user_id,
                        "note_link_id": str(note_link.id),
                        "operation": "get_note_link",
                    },
                )
                return note_link
            except NoteLinkNotFoundError as e:
                await uow.rollback()
                logger.warning(
                    f"Enlace no encontrado al intentar obtener (relanzando): {str(e)}",
                    extra={
                        "user_id": user_id,
                        "note_link_id": str(note_link_id),
                        "operation": "get_note_link",
                    },
                )
                e.context = e.context or {}
                e.context.update({"operation": "get_note_link"})
                raise
            except RepositoryError as e:
                await uow.rollback()
                logger.error(
                    f"Error de repositorio al obtener enlace: {str(e)}",
                    extra={
                        "user_id": user_id,
                        "note_link_id": str(note_link_id),
                        "operation": "get_note_link",
                        "error_message": str(e),
                    },
                )
                raise  # Re-lanzar RepositoryError
            except Exception as e:
                await uow.rollback()
                logger.exception(
                    f"Error inesperado al obtener enlace {note_link_id}: {str(e)}",
                    extra={
                        "user_id": user_id,
                        "note_link_id": str(note_link_id),
                        "operation": "get_note_link",
                    },
                )
                raise RepositoryError(
                    f"Error inesperado en el repositorio al obtener enlace: {str(e)}",
                    operation="get_note_link",
                    repository_type="NoteLinkRepository",
                    context={"note_link_id": str(note_link_id)},
                ) from e
