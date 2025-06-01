import logging
import uuid

from src.pkm_app.core.application.interfaces.unit_of_work_interface import (
    IUnitOfWork,
)
from src.pkm_app.core.domain.errors import (
    BusinessRuleViolationError,  # Importar el nuevo error
    EntityNotFoundError,
    PermissionDeniedError,
    RepositoryError,
    ValidationError,
)

# Configurar logger para este caso de uso
logger = logging.getLogger(__name__)


class DeleteKeywordUseCase:
    def __init__(self, unit_of_work: IUnitOfWork):
        self.unit_of_work = unit_of_work

    async def execute(self, keyword_id: uuid.UUID, user_id: str) -> bool:
        """
        Elimina una keyword.

        Args:
            keyword_id: ID de la keyword a eliminar.
            user_id: ID del usuario que elimina la keyword.

        Returns:
            True si la keyword fue eliminada.

        Raises:
            EntityNotFoundError: Si la keyword no se encuentra o no pertenece al usuario.
            PermissionDeniedError: Si no se proporciona el user_id o el usuario no tiene permisos.
            BusinessRuleViolationError: Si la keyword está asociada a notas y no puede ser eliminada.
            ValidationError: Si el keyword_id no es un UUID válido.
            RepositoryError: Si ocurre un error en la capa de persistencia.
        """
        logger.info(
            "Operación iniciada: Eliminar keyword",
            extra={
                "user_id": user_id,
                "keyword_id": str(keyword_id),
                "operation": "delete_keyword",
            },
        )

        if not user_id:
            logger.warning(
                "Intento de eliminación de keyword sin user_id.",
                extra={"keyword_id": str(keyword_id), "operation": "delete_keyword"},
            )
            raise PermissionDeniedError(
                "Se requiere ID de usuario para eliminar una keyword.",
                context={"operation": "delete_keyword"},
            )

        if not keyword_id:
            logger.warning(
                "Intento de eliminación de keyword sin keyword_id.",
                extra={"user_id": user_id, "operation": "delete_keyword"},
            )
            raise ValidationError(
                "Se requiere ID de keyword para eliminarla.",
                context={"field": "keyword_id", "operation": "delete_keyword"},
            )

        if not isinstance(keyword_id, uuid.UUID):
            logger.warning(
                f"Intento de eliminar keyword con ID inválido: {keyword_id}",
                extra={
                    "user_id": user_id,
                    "keyword_id": str(keyword_id),
                    "operation": "delete_keyword",
                },
            )
            raise ValidationError(
                f"El ID de la keyword debe ser un UUID válido. Valor recibido: {keyword_id}",
                context={"field": "keyword_id", "operation": "delete_keyword"},
            )

        async with self.unit_of_work as uow:
            try:
                # Verificar si la keyword existe y pertenece al usuario antes de intentar eliminar.
                # Esto también permite verificar reglas de negocio como la asociación con notas.
                keyword_to_delete = await uow.keywords.get_by_id(keyword_id, user_id)
                if not keyword_to_delete:
                    raise EntityNotFoundError(
                        f"Keyword con ID {keyword_id} no encontrada o no pertenece al usuario.",
                        entity_id=str(keyword_id),
                        entity_type="Keyword",
                        context={"operation": "delete_keyword", "user_id": user_id},
                    )

                # Lógica para verificar si la keyword está asociada a notas
                # Esto podría estar en el repositorio o aquí, dependiendo del diseño.
                # Por ahora, asumimos que el repositorio `delete` manejará esta lógica
                # y lanzará BusinessRuleViolationError si es necesario, o que se verifica aquí.
                # Para cumplir con test_specs_LS1_Keyword.md, el repositorio debe lanzar este error.
                # Si el repositorio no lo hace, se necesitaría una llamada adicional aquí:
                # associated_notes_count = await uow.keywords.count_notes_associated_with_keyword(keyword_id)
                # if associated_notes_count > 0:
                #     raise BusinessRuleViolationError(
                #         f"La keyword {keyword_id} no puede ser eliminada porque está asociada a {associated_notes_count} nota(s).",
                #         context={"keyword_id": str(keyword_id), "operation": "delete_keyword"}
                #     )

                # El método delete del repositorio debería lanzar EntityNotFoundError
                # si la nota no existe o no pertenece al usuario (ya cubierto por get_by_id).
                # Debería lanzar BusinessRuleViolationError si está asociada a notas.
                deleted = await uow.keywords.delete(keyword_id, user_id)

                if (
                    not deleted
                ):  # Si el repo devuelve False en lugar de lanzar error por no encontrarla
                    # Este caso es menos probable si get_by_id ya validó la existencia.
                    # Pero se mantiene por si el repo.delete tiene una lógica de no encontrado diferente.
                    raise EntityNotFoundError(
                        f"Keyword con ID {keyword_id} no pudo ser eliminada (no encontrada por el método delete).",
                        entity_id=str(keyword_id),
                        entity_type="Keyword",
                        context={"operation": "delete_keyword", "user_id": user_id},
                    )

                await uow.commit()

                logger.info(
                    f"Keyword {keyword_id} eliminada exitosamente",
                    extra={
                        "user_id": user_id,
                        "keyword_id": str(keyword_id),
                        "operation": "delete_keyword",
                    },
                )
                return True
            except EntityNotFoundError as e:
                await uow.rollback()
                logger.warning(
                    f"Keyword no encontrada al intentar eliminar: {str(e)}",
                    extra={
                        "user_id": user_id,
                        "keyword_id": str(keyword_id),
                        "operation": "delete_keyword",
                    },
                )
                e.context = e.context or {}
                e.context.update({"operation": "delete_keyword"})
                raise
            except PermissionDeniedError as e:  # Si el repositorio la lanza
                await uow.rollback()
                logger.warning(
                    f"Permiso denegado al eliminar keyword: {str(e)}",
                    extra={
                        "user_id": user_id,
                        "keyword_id": str(keyword_id),
                        "operation": "delete_keyword",
                    },
                )
                e.context = e.context or {}
                e.context.update({"operation": "delete_keyword"})
                raise
            except BusinessRuleViolationError as e:
                await uow.rollback()
                logger.warning(
                    f"Violación de regla de negocio al eliminar keyword: {str(e)}",
                    extra={
                        "user_id": user_id,
                        "keyword_id": str(keyword_id),
                        "operation": "delete_keyword",
                    },
                )
                # Re-lanzar con contexto de operación
                e.context = e.context or {}
                e.context.update({"operation": "delete_keyword"})
                raise
            except Exception as e:
                await uow.rollback()
                logger.exception(
                    f"Error inesperado al eliminar keyword {keyword_id}: {str(e)}",
                    extra={
                        "user_id": user_id,
                        "keyword_id": str(keyword_id),
                        "operation": "delete_keyword",
                    },
                )
                raise RepositoryError(
                    f"Error inesperado en el repositorio al eliminar keyword: {str(e)}",
                    operation="delete_keyword",
                    repository_type="KeywordRepository",
                    context={"keyword_id": str(keyword_id)},
                ) from e
