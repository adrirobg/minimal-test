import logging
import uuid

from src.pkm_app.core.application.dtos import KeywordSchema
from src.pkm_app.core.application.interfaces.unit_of_work_interface import (
    IUnitOfWork,
)
from src.pkm_app.core.domain.errors import (
    EntityNotFoundError,
    PermissionDeniedError,
    RepositoryError,
    ValidationError,
)

# Configurar logger para este caso de uso
logger = logging.getLogger(__name__)


class GetKeywordUseCase:
    def __init__(self, unit_of_work: IUnitOfWork):
        self.unit_of_work = unit_of_work

    async def execute(self, keyword_id: uuid.UUID, user_id: str) -> KeywordSchema:
        """
        Obtiene los detalles de una keyword específica.

        Args:
            keyword_id: ID de la keyword a obtener.
            user_id: ID del usuario que solicita la keyword.

        Returns:
            Los detalles de la keyword.

        Raises:
            EntityNotFoundError: Si la keyword no se encuentra o no pertenece al usuario.
            PermissionDeniedError: Si no se proporciona el user_id.
            ValidationError: Si el keyword_id no es un UUID válido.
            RepositoryError: Si ocurre un error en la capa de persistencia.
        """
        logger.info(
            "Operación iniciada: Obtener keyword",
            extra={
                "user_id": user_id,
                "keyword_id": str(keyword_id),
                "operation": "get_keyword",
            },
        )

        if not user_id:
            logger.warning(
                "Intento de obtener keyword sin user_id.",
                extra={"keyword_id": str(keyword_id), "operation": "get_keyword"},
            )
            raise PermissionDeniedError(
                "Se requiere ID de usuario para obtener una keyword.",
                context={"operation": "get_keyword"},
            )

        if not keyword_id:
            logger.warning(
                "Intento de obtener keyword sin keyword_id.",
                extra={"user_id": user_id, "operation": "get_keyword"},
            )
            raise ValidationError(
                "Se requiere ID de keyword para obtenerla.",
                context={"field": "keyword_id", "operation": "get_keyword"},
            )

        if not isinstance(keyword_id, uuid.UUID):
            logger.warning(
                f"Intento de obtener keyword con ID inválido: {keyword_id}",
                extra={
                    "user_id": user_id,
                    "keyword_id": str(keyword_id),
                    "operation": "get_keyword",
                },
            )
            raise ValidationError(
                f"El ID de la keyword debe ser un UUID válido. Valor recibido: {keyword_id}",
                context={"field": "keyword_id", "operation": "get_keyword"},
            )

        async with self.unit_of_work as uow:
            try:
                keyword = await uow.keywords.get_by_id(
                    entity_id=keyword_id, user_id=user_id
                )  # Ajustado a entity_id
                if not keyword:
                    logger.warning(
                        f"Keyword {keyword_id} no encontrada por el repositorio para el usuario {user_id}.",
                        extra={
                            "user_id": user_id,
                            "keyword_id": str(keyword_id),
                            "operation": "get_keyword",
                        },
                    )
                    raise EntityNotFoundError(  # Usando EntityNotFoundError genérico
                        f"Keyword con ID {keyword_id} no encontrada o no pertenece al usuario.",
                        entity_id=str(keyword_id),  # Convertido a string para el contexto
                        entity_type="Keyword",
                        context={"operation": "get_keyword", "user_id": user_id},
                    )

                logger.info(
                    f"Keyword {keyword.id} obtenida exitosamente",
                    extra={
                        "user_id": user_id,
                        "keyword_id": str(keyword.id),
                        "operation": "get_keyword",
                    },
                )
                return keyword
            except EntityNotFoundError as e:
                await uow.rollback()
                logger.warning(
                    f"Keyword no encontrada al intentar obtener (relanzando): {str(e)}",
                    extra={
                        "user_id": user_id,
                        "keyword_id": str(keyword_id),
                        "operation": "get_keyword",
                    },
                )
                e.context = e.context or {}
                e.context.update({"operation": "get_keyword"})
                raise
            except Exception as e:
                await uow.rollback()
                logger.exception(
                    f"Error inesperado al obtener keyword {keyword_id}: {str(e)}",
                    extra={
                        "user_id": user_id,
                        "keyword_id": str(keyword_id),
                        "operation": "get_keyword",
                    },
                )
                raise RepositoryError(
                    f"Error inesperado en el repositorio al obtener keyword: {str(e)}",
                    operation="get_keyword",
                    repository_type="KeywordRepository",
                    context={"keyword_id": str(keyword_id)},
                ) from e
