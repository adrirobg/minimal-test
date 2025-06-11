import logging
import uuid

from src.pkm_app.core.application.interfaces.unit_of_work_interface import (
    IUnitOfWork,
)
from src.pkm_app.core.domain.errors import (
    PermissionDeniedError,
    RepositoryError,
    SourceNotFoundError,
    ValidationError,
)

# Configurar logger para este caso de uso
logger = logging.getLogger(__name__)


class DeleteSourceUseCase:
    def __init__(self, unit_of_work: IUnitOfWork):
        self.unit_of_work = unit_of_work

    async def execute(self, source_id: uuid.UUID, user_id: str) -> bool:
        """
        Elimina una fuente.

        Args:
            source_id: ID de la fuente a eliminar.
            user_id: ID del usuario que elimina la fuente.

        Returns:
            True si la fuente fue eliminada.

        Raises:
            SourceNotFoundError: Si la fuente no se encuentra o no pertenece al usuario.
            PermissionDeniedError: Si no se proporciona el user_id.
            ValidationError: Si el source_id no es un UUID válido.
            RepositoryError: Si ocurre un error en la capa de persistencia.
        """
        logger.info(
            "Operación iniciada: Eliminar fuente",
            extra={
                "user_id": user_id,
                "source_id": str(source_id),
                "operation": "delete_source",
            },
        )

        if not user_id:
            logger.warning(
                "Intento de eliminación de fuente sin user_id.",
                extra={"source_id": str(source_id), "operation": "delete_source"},
            )
            raise PermissionDeniedError(
                "Se requiere ID de usuario para eliminar una fuente.",
                context={"operation": "delete_source"},
            )

        if not isinstance(source_id, uuid.UUID):
            logger.warning(
                f"Intento de eliminar fuente con source_id inválido: {source_id}.",
                extra={
                    "user_id": user_id,
                    "operation": "delete_source",
                    "invalid_source_id": str(source_id),
                },
            )
            raise ValidationError(
                "El ID de la fuente debe ser un UUID válido.",
                context={"field": "source_id", "operation": "delete_source"},
            )

        async with self.unit_of_work as uow:
            try:
                # Se asume que el repositorio de fuentes tiene un método `delete`
                # que lanza SourceNotFoundError si la fuente no existe o no pertenece al usuario.
                await uow.sources.delete(source_id=source_id, user_id=user_id)
                await uow.commit()

                logger.info(
                    f"Fuente {source_id} eliminada exitosamente",
                    extra={
                        "user_id": user_id,
                        "source_id": str(source_id),
                        "operation": "delete_source",
                    },
                )
                return True
            except SourceNotFoundError as e:
                await uow.rollback()
                logger.warning(
                    f"Fuente no encontrada al intentar eliminar: {str(e)}",
                    extra={
                        "user_id": user_id,
                        "source_id": str(source_id),
                        "operation": "delete_source",
                    },
                )
                raise SourceNotFoundError(
                    str(e), source_id=source_id, context={"operation": "delete_source"}
                ) from e
            except Exception as e:
                await uow.rollback()
                logger.exception(
                    f"Error inesperado al eliminar fuente {source_id}: {str(e)}",
                    extra={
                        "user_id": user_id,
                        "source_id": str(source_id),
                        "operation": "delete_source",
                    },
                )
                raise RepositoryError(
                    f"Error inesperado en el repositorio al eliminar fuente: {str(e)}",
                    operation="delete_source",
                    repository_type="SourceRepository",
                    context={"source_id": str(source_id)},
                ) from e
