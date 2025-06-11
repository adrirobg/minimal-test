import logging
import uuid

from src.pkm_app.core.application.dtos import SourceCreate, SourceSchema
from src.pkm_app.core.application.interfaces.unit_of_work_interface import (
    IUnitOfWork,
)
from src.pkm_app.core.domain.errors import PermissionDeniedError, RepositoryError, ValidationError

# Configurar logger para este caso de uso
logger = logging.getLogger(__name__)


class CreateSourceUseCase:
    def __init__(self, unit_of_work: IUnitOfWork):
        self.unit_of_work = unit_of_work

    async def execute(self, source_in: SourceCreate, user_id: str) -> SourceSchema:
        """
        Crea una nueva fuente.

        Args:
            source_in: Datos para crear la fuente.
            user_id: ID del usuario que crea la fuente.

        Returns:
            La fuente creada.

        Raises:
            ValidationError: Si los datos de entrada son inválidos.
            PermissionDeniedError: Si el usuario no tiene permisos.
            RepositoryError: Si ocurre un error en la capa de persistencia.
        """
        logger.info(
            "Operación iniciada: Crear fuente",
            extra={"user_id": user_id, "operation": "create_source"},
        )

        if not user_id:
            logger.warning(
                "Intento de creación de fuente sin user_id.",
                extra={"operation": "create_source"},
            )
            raise PermissionDeniedError(
                "Se requiere ID de usuario para crear una fuente.",
                context={"operation": "create_source"},
            )

        if not source_in.title:
            logger.warning(
                "Intento de creación de fuente con título vacío.",
                extra={"user_id": user_id, "operation": "create_source"},
            )
            raise ValidationError(
                "El título de la fuente no puede estar vacío.",
                context={"field": "title", "operation": "create_source"},
            )
        # Validar que si se proporciona url, no sea string vacío
        if hasattr(source_in, "url") and source_in.url == "":
            logger.warning(
                "Intento de creación de fuente con URL vacía.",
                extra={"user_id": user_id, "operation": "create_source"},
            )
            raise ValidationError(
                "La URL de la fuente no puede ser vacía.",
                context={"field": "url", "operation": "create_source"},
            )

        async with self.unit_of_work as uow:
            try:
                # Aquí se asume que el repositorio de fuentes tiene un método `create`
                # similar al de notas, que maneja la lógica de creación y pertenencia.
                created_source_schema = await uow.sources.create(
                    source_in=source_in, user_id=user_id
                )
                await uow.commit()

                logger.info(
                    f"Fuente creada exitosamente con ID {created_source_schema.id}",
                    extra={
                        "user_id": user_id,
                        "source_id": str(created_source_schema.id),
                        "operation": "create_source",
                    },
                )
                return created_source_schema
            except ValueError as e:
                await uow.rollback()
                logger.warning(
                    f"Error de validación al crear fuente: {str(e)}",
                    extra={
                        "user_id": user_id,
                        "operation": "create_source",
                        "error_message": str(e),
                    },
                )
                raise ValidationError(str(e), context={"operation": "create_source"}) from e
            except Exception as e:
                await uow.rollback()
                logger.exception(
                    f"Error inesperado al crear fuente: {str(e)}",
                    extra={"user_id": user_id, "operation": "create_source"},
                )
                raise RepositoryError(
                    f"Error inesperado en el repositorio al crear fuente: {str(e)}",
                    operation="create_source",
                    repository_type="SourceRepository",
                ) from e
