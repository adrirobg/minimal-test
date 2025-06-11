import logging
import uuid

from src.pkm_app.core.application.dtos import KeywordSchema, KeywordUpdate
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


class UpdateKeywordUseCase:
    def __init__(self, unit_of_work: IUnitOfWork):
        self.unit_of_work = unit_of_work

    async def execute(
        self, keyword_id: uuid.UUID, keyword_in: KeywordUpdate, user_id: str
    ) -> KeywordSchema:
        """
        Actualiza una keyword existente.

        Args:
            keyword_id: ID de la keyword a actualizar.
            keyword_in: Datos para actualizar la keyword.
            user_id: ID del usuario que actualiza la keyword.

        Returns:
            La keyword actualizada.

        Raises:
            EntityNotFoundError: Si la keyword no se encuentra o no pertenece al usuario.
            ValidationError: Si los datos de entrada son inválidos.
            PermissionDeniedError: Si no se proporciona el user_id o el usuario no tiene permisos.
            RepositoryError: Si ocurre un error en la capa de persistencia.
        """
        logger.info(
            "Operación iniciada: Actualizar keyword",
            extra={
                "user_id": user_id,
                "keyword_id": str(keyword_id),
                "operation": "update_keyword",
            },
        )

        if not user_id:
            logger.warning(
                "Intento de actualización de keyword sin user_id.",
                extra={"keyword_id": str(keyword_id), "operation": "update_keyword"},
            )
            raise PermissionDeniedError(
                "Se requiere ID de usuario para actualizar una keyword.",
                context={"operation": "update_keyword"},
            )

        if not keyword_id:
            logger.warning(
                "Intento de actualización de keyword sin keyword_id.",
                extra={"user_id": user_id, "operation": "update_keyword"},
            )
            raise ValidationError(
                "Se requiere ID de keyword para actualizarla.",
                context={"field": "keyword_id", "operation": "update_keyword"},
            )

        if not isinstance(keyword_id, uuid.UUID):
            logger.warning(
                f"Intento de actualizar keyword con ID inválido: {keyword_id}",
                extra={
                    "user_id": user_id,
                    "keyword_id": str(keyword_id),
                    "operation": "update_keyword",
                },
            )
            raise ValidationError(
                f"El ID de la keyword debe ser un UUID válido. Valor recibido: {keyword_id}",
                context={"field": "keyword_id", "operation": "update_keyword"},
            )

        if keyword_in.name is not None and not keyword_in.name.strip():
            logger.warning(
                "Intento de actualización de keyword con nombre vacío.",
                extra={
                    "user_id": user_id,
                    "keyword_id": str(keyword_id),
                    "operation": "update_keyword",
                },
            )
            raise ValidationError(
                "El nombre de la keyword no puede estar vacío si se proporciona para actualizar.",
                context={"field": "name", "operation": "update_keyword"},
            )

        async with self.unit_of_work as uow:
            try:
                # Primero, verificar si la keyword existe y pertenece al usuario
                existing_keyword = await uow.keywords.get_by_id(keyword_id, user_id)
                if not existing_keyword:
                    raise EntityNotFoundError(
                        f"Keyword con ID {keyword_id} no encontrada o no pertenece al usuario.",
                        entity_id=str(keyword_id),
                        entity_type="Keyword",
                        context={"operation": "update_keyword", "user_id": user_id},
                    )

                # El método update del repositorio se encargará de la lógica de actualización
                # y de verificar si el usuario tiene permiso (si es necesario, aunque get_by_id ya lo hizo)
                updated_keyword = await uow.keywords.update(keyword_id, keyword_in, user_id)
                # El repositorio debería lanzar EntityNotFoundError si no la encuentra durante el update,
                # o PermissionDeniedError si el user_id no coincide (aunque ya lo validamos antes).
                # Si devuelve None, también lo manejamos como no encontrado.
                if updated_keyword is None:  # Doble check, aunque el repo debería lanzar error
                    raise EntityNotFoundError(
                        f"Keyword con ID {keyword_id} no encontrada durante la actualización.",
                        entity_id=str(keyword_id),
                        entity_type="Keyword",
                        context={"operation": "update_keyword", "user_id": user_id},
                    )

                await uow.commit()

                logger.info(
                    f"Keyword {updated_keyword.id} actualizada exitosamente",
                    extra={
                        "user_id": user_id,
                        "keyword_id": str(updated_keyword.id),
                        "operation": "update_keyword",
                    },
                )
                return updated_keyword
            except EntityNotFoundError as e:
                await uow.rollback()
                logger.warning(
                    f"Keyword no encontrada al intentar actualizar: {str(e)}",
                    extra={
                        "user_id": user_id,
                        "keyword_id": str(keyword_id),
                        "operation": "update_keyword",
                    },
                )
                e.context = e.context or {}
                e.context.update({"operation": "update_keyword"})
                raise
            except PermissionDeniedError as e:  # Si el repositorio la lanza por alguna razón
                await uow.rollback()
                logger.warning(
                    f"Permiso denegado al actualizar keyword: {str(e)}",
                    extra={
                        "user_id": user_id,
                        "keyword_id": str(keyword_id),
                        "operation": "update_keyword",
                    },
                )
                e.context = e.context or {}
                e.context.update({"operation": "update_keyword"})
                raise
            except ValueError as e:  # Errores de validación del repositorio (ej: nombre duplicado)
                await uow.rollback()
                logger.warning(
                    f"Error de validación al actualizar keyword: {str(e)}",
                    extra={
                        "user_id": user_id,
                        "keyword_id": str(keyword_id),
                        "operation": "update_keyword",
                        "error_message": str(e),
                        "update_data_name": keyword_in.name,
                    },
                )
                raise ValidationError(
                    f"Error de validación al actualizar keyword: {str(e)}",
                    context={"operation": "update_keyword"},
                ) from e
            except Exception as e:
                await uow.rollback()
                logger.exception(
                    f"Error inesperado al actualizar keyword {keyword_id}: {str(e)}",
                    extra={
                        "user_id": user_id,
                        "keyword_id": str(keyword_id),
                        "operation": "update_keyword",
                    },
                )
                raise RepositoryError(
                    f"Error inesperado en el repositorio al actualizar keyword: {str(e)}",
                    operation="update_keyword",
                    repository_type="KeywordRepository",
                    context={"keyword_id": str(keyword_id)},
                ) from e
