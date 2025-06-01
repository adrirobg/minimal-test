import logging
import uuid

from src.pkm_app.core.application.dtos import SourceSchema
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


class GetSourceUseCase:
    def __init__(self, unit_of_work: IUnitOfWork):
        self.unit_of_work = unit_of_work

    async def execute(self, source_id: uuid.UUID, user_id: str) -> SourceSchema:
        """
        Obtiene los detalles de una fuente específica.

        Args:
            source_id: ID de la fuente a obtener.
            user_id: ID del usuario que solicita la fuente.

        Returns:
            Los detalles de la fuente.

        Raises:
            SourceNotFoundError: Si la fuente no se encuentra o no pertenece al usuario.
            PermissionDeniedError: Si no se proporciona el user_id.
            ValidationError: Si el source_id no es un UUID válido.
            RepositoryError: Si ocurre un error en la capa de persistencia.
        """
        logger.info(
            "Operación iniciada: Obtener fuente",
            extra={
                "user_id": user_id,
                "source_id": str(source_id),
                "operation": "get_source",
            },
        )

        if not user_id:
            logger.warning(
                "Intento de obtener fuente sin user_id.",
                extra={"source_id": str(source_id), "operation": "get_source"},
            )
            raise PermissionDeniedError(
                "Se requiere ID de usuario para obtener una fuente.",
                context={"operation": "get_source"},
            )

        if not isinstance(source_id, uuid.UUID):
            logger.warning(
                f"Intento de obtener fuente con source_id inválido: {source_id}.",
                extra={
                    "user_id": user_id,
                    "operation": "get_source",
                    "invalid_source_id": str(source_id),
                },
            )
            raise ValidationError(
                "El ID de la fuente debe ser un UUID válido.",
                context={"field": "source_id", "operation": "get_source"},
            )

        async with self.unit_of_work as uow:
            try:
                source = await uow.sources.get_by_id(source_id=source_id, user_id=user_id)
                if not source:
                    logger.warning(
                        f"Fuente {source_id} no encontrada por el repositorio para el usuario {user_id}.",
                        extra={
                            "user_id": user_id,
                            "source_id": str(source_id),
                            "operation": "get_source",
                        },
                    )
                    raise SourceNotFoundError(
                        f"Fuente con ID {source_id} no encontrada o no pertenece al usuario.",
                        source_id=source_id,
                        context={"operation": "get_source", "user_id": user_id},
                    )

                logger.info(
                    f"Fuente {source.id} obtenida exitosamente",
                    extra={
                        "user_id": user_id,
                        "source_id": str(source.id),
                        "operation": "get_source",
                    },
                )
                return source
            except SourceNotFoundError as e:
                await uow.rollback()
                logger.warning(
                    f"Fuente no encontrada al intentar obtener (relanzando): {str(e)}",
                    extra={
                        "user_id": user_id,
                        "source_id": str(source_id),
                        "operation": "get_source",
                    },
                )
                e.context = e.context or {}
                e.context.update({"operation": "get_source"})
                raise
            except Exception as e:
                await uow.rollback()
                logger.exception(
                    f"Error inesperado al obtener fuente {source_id}: {str(e)}",
                    extra={
                        "user_id": user_id,
                        "source_id": str(source_id),
                        "operation": "get_source",
                    },
                )
                raise RepositoryError(
                    f"Error inesperado en el repositorio al obtener fuente: {str(e)}",
                    operation="get_source",
                    repository_type="SourceRepository",
                    context={"source_id": str(source_id)},
                ) from e
