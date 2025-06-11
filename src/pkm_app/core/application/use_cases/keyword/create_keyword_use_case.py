import logging
import uuid

from src.pkm_app.core.application.dtos import KeywordCreate, KeywordSchema
from src.pkm_app.core.application.interfaces.unit_of_work_interface import (
    IUnitOfWork,
)
from src.pkm_app.core.domain.errors import PermissionDeniedError, RepositoryError, ValidationError

# Configurar logger para este caso de uso
logger = logging.getLogger(__name__)


class CreateKeywordUseCase:
    def __init__(self, unit_of_work: IUnitOfWork):
        self.unit_of_work = unit_of_work

    async def execute(self, keyword_in: KeywordCreate, user_id: str) -> KeywordSchema:
        """
        Crea una nueva keyword.

        Args:
            keyword_in: Datos para crear la keyword.
            user_id: ID del usuario que crea la keyword.

        Returns:
            La keyword creada.

        Raises:
            ValidationError: Si los datos de entrada son inválidos.
            PermissionDeniedError: Si el usuario no tiene permisos.
            RepositoryError: Si ocurre un error en la capa de persistencia.
        """
        logger.info(
            "Operación iniciada: Crear keyword",
            extra={"user_id": user_id, "operation": "create_keyword"},
        )

        if not user_id:
            logger.warning(
                "Intento de creación de keyword sin user_id.",
                extra={"operation": "create_keyword"},
            )
            raise PermissionDeniedError(
                "Se requiere ID de usuario para crear una keyword.",
                context={"operation": "create_keyword"},
            )

        if not keyword_in.name or not keyword_in.name.strip():
            logger.warning(
                "Intento de creación de keyword con nombre vacío.",
                extra={"user_id": user_id, "operation": "create_keyword"},
            )
            raise ValidationError(
                "El nombre de la keyword no puede estar vacío.",
                context={"field": "name", "operation": "create_keyword"},
            )

        async with self.unit_of_work as uow:
            try:
                created_keyword_schema = await uow.keywords.create(
                    keyword_in=keyword_in, user_id=user_id
                )
                await uow.commit()

                logger.info(
                    f"Keyword creada exitosamente con ID {created_keyword_schema.id}",
                    extra={
                        "user_id": user_id,
                        "keyword_id": str(created_keyword_schema.id),
                        "operation": "create_keyword",
                    },
                )
                return created_keyword_schema
            except (
                ValueError
            ) as e:  # Asumiendo que el repositorio puede lanzar ValueError por duplicados u otras validaciones
                await uow.rollback()
                logger.warning(
                    f"Error de validación al crear keyword: {str(e)}",
                    extra={
                        "user_id": user_id,
                        "operation": "create_keyword",
                        "error_message": str(e),
                        "keyword_name": keyword_in.name,
                    },
                )
                # Podría ser un error de duplicado si el repositorio lo maneja así.
                # O podría ser una validación más específica del repositorio.
                raise ValidationError(
                    f"Error al crear la keyword: {str(e)}", context={"operation": "create_keyword"}
                ) from e
            except Exception as e:
                await uow.rollback()
                logger.exception(
                    f"Error inesperado al crear keyword: {str(e)}",
                    extra={"user_id": user_id, "operation": "create_keyword"},
                )
                raise RepositoryError(
                    f"Error inesperado en el repositorio al crear keyword: {str(e)}",
                    operation="create_keyword",
                    repository_type="KeywordRepository",
                ) from e
