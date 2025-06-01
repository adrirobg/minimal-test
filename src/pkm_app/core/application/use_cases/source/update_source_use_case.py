import logging
import uuid

from src.pkm_app.core.application.dtos import SourceSchema, SourceUpdate
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


class UpdateSourceUseCase:
    def __init__(self, unit_of_work: IUnitOfWork):
        self.unit_of_work = unit_of_work

    async def execute(
        self, source_id: uuid.UUID, source_in: SourceUpdate, user_id: str
    ) -> SourceSchema:
        """
        Actualiza una fuente existente.

        Args:
            source_id: ID de la fuente a actualizar.
            source_in: Datos para actualizar la fuente.
            user_id: ID del usuario que actualiza la fuente.

        Returns:
            La fuente actualizada.

        Raises:
            SourceNotFoundError: Si la fuente no se encuentra o no pertenece al usuario.
            ValidationError: Si los datos de entrada son inválidos.
            PermissionDeniedError: Si no se proporciona el user_id.
            RepositoryError: Si ocurre un error en la capa de persistencia.
        """
        logger.info(
            "Operación iniciada: Actualizar fuente",
            extra={
                "user_id": user_id,
                "source_id": str(source_id),
                "operation": "update_source",
            },
        )

        if not user_id:
            logger.warning(
                "Intento de actualización de fuente sin user_id.",
                extra={"source_id": str(source_id), "operation": "update_source"},
            )
            raise PermissionDeniedError(
                "Se requiere ID de usuario para actualizar una fuente.",
                context={"operation": "update_source"},
            )

        if not isinstance(source_id, uuid.UUID):
            logger.warning(
                f"Intento de actualizar fuente con source_id inválido: {source_id}.",
                extra={
                    "user_id": user_id,
                    "operation": "update_source",
                    "invalid_source_id": str(source_id),
                },
            )
            raise ValidationError(
                "El ID de la fuente debe ser un UUID válido.",
                context={"field": "source_id", "operation": "update_source"},
            )

        # Validar que al menos un campo se está actualizando
        if not source_in.model_fields_set:
            logger.warning(
                "Intento de actualización de fuente sin datos para actualizar.",
                extra={
                    "user_id": user_id,
                    "source_id": str(source_id),
                    "operation": "update_source",
                },
            )
            raise ValidationError(
                "No se proporcionaron datos para actualizar la fuente.",
                context={"operation": "update_source"},
            )

        # Validar que si se actualiza title, no sea vacío
        if hasattr(source_in, "title") and source_in.title == "":
            logger.warning(
                "Intento de actualización de fuente con título vacío.",
                extra={
                    "user_id": user_id,
                    "source_id": str(source_id),
                    "operation": "update_source",
                },
            )
            raise ValidationError(
                "El título de la fuente no puede ser vacío si se actualiza.",
                context={"field": "title", "operation": "update_source"},
            )
        # Validar que si se actualiza url, no sea string vacío
        if hasattr(source_in, "url") and source_in.url == "":
            logger.warning(
                "Intento de actualización de fuente con URL vacía.",
                extra={
                    "user_id": user_id,
                    "source_id": str(source_id),
                    "operation": "update_source",
                },
            )
            raise ValidationError(
                "La URL de la fuente no puede ser vacía si se actualiza.",
                context={"field": "url", "operation": "update_source"},
            )

        async with self.unit_of_work as uow:
            try:
                updated_source = await uow.sources.update(
                    source_id=source_id, source_in=source_in, user_id=user_id
                )
                if updated_source is None:
                    await uow.rollback()
                    logger.warning(
                        f"Fuente no encontrada al intentar actualizar: {source_id}",
                        extra={
                            "user_id": user_id,
                            "source_id": str(source_id),
                            "operation": "update_source",
                        },
                    )
                    raise SourceNotFoundError(
                        f"Fuente no encontrada: {source_id}",
                        source_id=source_id,
                        context={"operation": "update_source"},
                    )
                await uow.commit()

                logger.info(
                    f"Fuente {updated_source.id} actualizada exitosamente",
                    extra={
                        "user_id": user_id,
                        "source_id": str(updated_source.id),
                        "operation": "update_source",
                    },
                )
                return updated_source
            except SourceNotFoundError as e:
                await uow.rollback()
                logger.warning(
                    f"Fuente no encontrada al intentar actualizar: {str(e)}",
                    extra={
                        "user_id": user_id,
                        "source_id": str(source_id),
                        "operation": "update_source",
                    },
                )
                raise SourceNotFoundError(
                    str(e), source_id=source_id, context={"operation": "update_source"}
                ) from e
            except ValueError as e:  # Errores de validación desde el repositorio
                await uow.rollback()
                logger.warning(
                    f"Error de validación al actualizar fuente: {str(e)}",
                    extra={
                        "user_id": user_id,
                        "source_id": str(source_id),
                        "operation": "update_source",
                        "error_message": str(e),
                    },
                )
                raise ValidationError(str(e), context={"operation": "update_source"}) from e
            except Exception as e:
                await uow.rollback()
                logger.exception(
                    f"Error inesperado al actualizar fuente {source_id}: {str(e)}",
                    extra={
                        "user_id": user_id,
                        "source_id": str(source_id),
                        "operation": "update_source",
                    },
                )
                raise RepositoryError(
                    f"Error inesperado en el repositorio al actualizar fuente: {str(e)}",
                    operation="update_source",
                    repository_type="SourceRepository",
                    context={"source_id": str(source_id)},
                ) from e
