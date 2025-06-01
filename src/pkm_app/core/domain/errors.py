"""
Este módulo define excepciones específicas del dominio para el sistema PKM.

Las excepciones en este módulo proporcionan información clara sobre errores
de dominio y son utilizadas por los casos de uso y otras capas de la aplicación
para manejar situaciones excepcionales de manera consistente.
"""

import logging
from typing import Any, Optional

# Configurar el logger para los errores de dominio
logger = logging.getLogger(__name__)


class DomainError(Exception):
    """
    Excepción base para todos los errores relacionados con el dominio.

    Proporciona funcionalidad común para el registro de errores y la
    inclusión de contexto adicional para depuración.
    """

    def __init__(
        self, message: str, context: dict[str, Any] | None = None, log_level: int = logging.ERROR
    ):
        """
        Inicializa una nueva instancia de DomainError.

        Args:
            message: Mensaje descriptivo del error.
            context: Diccionario opcional con información de contexto adicional.
            log_level: Nivel de registro para este error (default: ERROR).
        """
        self.message = message
        self.context = context or {}
        super().__init__(message)

        # Registrar el error en el log con el nivel especificado
        self._log_error(log_level)

    def _log_error(self, level: int) -> None:
        """
        Registra el error en el sistema de logs.

        Args:
            level: Nivel de logging para este error.
        """
        error_class = self.__class__.__name__
        log_message = f"{error_class}: {self.message}"

        if self.context:
            log_message += f" | Contexto: {self.context}"

        logger.log(level, log_message)


class ValidationError(DomainError):
    """
    Error que se produce cuando los datos de entrada no cumplen con las reglas de validación.

    Ejemplos:
    - Datos obligatorios faltantes
    - Formato incorrecto
    - Valores fuera de rango permitido
    """

    def __init__(self, message: str, context: dict[str, Any] | None = None):
        """
        Inicializa un nuevo error de validación.

        Args:
            message: Mensaje descriptivo del error de validación.
            context: Diccionario opcional con información de contexto adicional.
        """
        super().__init__(message, context, logging.WARNING)


class ResourceNotFoundError(DomainError):
    """
    Error base que se produce cuando un recurso solicitado no se encuentra.

    Esta es una clase base para errores más específicos de recursos no encontrados.
    """

    def __init__(
        self,
        message: str,
        resource_id: Any | None = None,
        resource_type: str | None = None,
        context: dict[str, Any] | None = None,
    ):
        """
        Inicializa un nuevo error de recurso no encontrado.

        Args:
            message: Mensaje descriptivo del error.
            resource_id: Identificador opcional del recurso no encontrado.
            resource_type: Tipo opcional del recurso no encontrado.
            context: Diccionario opcional con información de contexto adicional.
        """
        ctx = context or {}
        if resource_id is not None:
            ctx["resource_id"] = str(resource_id)
        if resource_type is not None:
            ctx["resource_type"] = resource_type

        super().__init__(message, ctx, logging.WARNING)


class NoteNotFoundError(ResourceNotFoundError):
    """
    Error que se produce cuando una nota solicitada no se encuentra o no pertenece al usuario.
    """

    def __init__(
        self, message: str, note_id: Any | None = None, context: dict[str, Any] | None = None
    ):
        """
        Inicializa un nuevo error de nota no encontrada.

        Args:
            message: Mensaje descriptivo del error.
            note_id: Identificador opcional de la nota no encontrada.
            context: Diccionario opcional con información de contexto adicional.
        """
        super().__init__(message, resource_id=note_id, resource_type="Note", context=context)


class ProjectNotFoundError(ResourceNotFoundError):
    """
    Error que se produce cuando un proyecto solicitado no se encuentra o no pertenece al usuario.
    """

    def __init__(
        self,
        message: str,
        project_id: Any | None = None,
        context: dict[str, Any] | None = None,
    ):
        """
        Inicializa un nuevo error de proyecto no encontrado.

        Args:
            message: Mensaje descriptivo del error.
            project_id: Identificador opcional del proyecto no encontrado.
            context: Diccionario opcional con información de contexto adicional.
        """
        super().__init__(message, resource_id=project_id, resource_type="Project", context=context)


class SourceNotFoundError(ResourceNotFoundError):
    """
    Error que se produce cuando una fuente solicitada no se encuentra o no pertenece al usuario.
    """

    def __init__(
        self,
        message: str,
        source_id: Any | None = None,
        context: dict[str, Any] | None = None,
    ):
        """
        Inicializa un nuevo error de fuente no encontrada.

        Args:
            message: Mensaje descriptivo del error.
            source_id: Identificador opcional de la fuente no encontrada.
            context: Diccionario opcional con información de contexto adicional.
        """
        super().__init__(message, resource_id=source_id, resource_type="Source", context=context)


class KeywordNotFoundError(ResourceNotFoundError):
    """
    Error que se produce cuando una palabra clave solicitada no se encuentra.
    """

    def __init__(
        self,
        message: str,
        keyword_id: Any | None = None,
        context: dict[str, Any] | None = None,
    ):
        """
        Inicializa un nuevo error de palabra clave no encontrada.

        Args:
            message: Mensaje descriptivo del error.
            keyword_id: Identificador opcional de la palabra clave no encontrada.
            context: Diccionario opcional con información de contexto adicional.
        """
        super().__init__(message, resource_id=keyword_id, resource_type="Keyword", context=context)


class NoteLinkNotFoundError(ResourceNotFoundError):
    """
    Error que se produce cuando un enlace entre notas solicitado no se encuentra.
    """

    def __init__(
        self, message: str, link_id: Any | None = None, context: dict[str, Any] | None = None
    ):
        """
        Inicializa un nuevo error de enlace entre notas no encontrado.

        Args:
            message: Mensaje descriptivo del error.
            link_id: Identificador opcional del enlace no encontrado.
            context: Diccionario opcional con información de contexto adicional.
        """
        super().__init__(message, resource_id=link_id, resource_type="NoteLink", context=context)


class PermissionDeniedError(DomainError):
    """
    Error que se produce cuando un usuario intenta acceder a un recurso
    para el cual no tiene permisos.
    """

    def __init__(
        self,
        message: str,
        user_id: str | None = None,
        resource_id: Any | None = None,
        resource_type: str | None = None,
        context: dict[str, Any] | None = None,
    ):
        """
        Inicializa un nuevo error de permiso denegado.

        Args:
            message: Mensaje descriptivo del error.
            user_id: Identificador opcional del usuario.
            resource_id: Identificador opcional del recurso.
            resource_type: Tipo opcional del recurso.
            context: Diccionario opcional con información de contexto adicional.
        """
        ctx = context or {}
        if user_id is not None:
            ctx["user_id"] = user_id
        if resource_id is not None:
            ctx["resource_id"] = str(resource_id)
        if resource_type is not None:
            ctx["resource_type"] = resource_type

        super().__init__(message, ctx, logging.WARNING)


class BusinessRuleViolationError(DomainError):
    """
    Error que se produce cuando se viola una regla de negocio del dominio.

    Ejemplos:
    - Intentar crear relaciones circulares entre notas
    - Exceder el número máximo de notas por proyecto
    - Intentar modificar datos que están en uso por otro proceso
    """

    def __init__(
        self,
        message: str,
        rule_name: str | None = None,
        context: dict[str, Any] | None = None,
    ):
        """
        Inicializa un nuevo error de violación de regla de negocio.

        Args:
            message: Mensaje descriptivo del error.
            rule_name: Nombre opcional de la regla violada.
            context: Diccionario opcional con información de contexto adicional.
        """
        ctx = context or {}
        if rule_name is not None:
            ctx["rule_name"] = rule_name

        super().__init__(message, ctx, logging.ERROR)


class ConcurrencyError(DomainError):
    """
    Error que se produce cuando hay un conflicto de concurrencia al modificar un recurso.

    Ejemplos:
    - Intentar actualizar un recurso que ha sido modificado por otro proceso
    - Problemas de bloqueo o deadlock
    """

    def __init__(
        self,
        message: str,
        resource_id: Any | None = None,
        resource_type: str | None = None,
        context: dict[str, Any] | None = None,
    ):
        """
        Inicializa un nuevo error de concurrencia.

        Args:
            message: Mensaje descriptivo del error.
            resource_id: Identificador opcional del recurso.
            resource_type: Tipo opcional del recurso.
            context: Diccionario opcional con información de contexto adicional.
        """
        ctx = context or {}
        if resource_id is not None:
            ctx["resource_id"] = str(resource_id)
        if resource_type is not None:
            ctx["resource_type"] = resource_type

        super().__init__(message, ctx, logging.ERROR)


class RepositoryError(DomainError):
    """
    Error que se produce cuando hay un problema en la capa de repositorio.

    Ejemplos:
    - Problemas de conexión con la base de datos
    - Errores en consultas
    - Problemas de integridad referencial
    """

    def __init__(
        self,
        message: str,
        operation: str | None = None,
        repository_type: str | None = None,
        context: dict[str, Any] | None = None,
    ):
        """
        Inicializa un nuevo error de repositorio.

        Args:
            message: Mensaje descriptivo del error.
            operation: Operación opcional que se estaba realizando.
            repository_type: Tipo opcional del repositorio.
            context: Diccionario opcional con información de contexto adicional.
        """
        ctx = context or {}
        if operation is not None:
            ctx["operation"] = operation
        if repository_type is not None:
            ctx["repository_type"] = repository_type

        super().__init__(message, ctx, logging.ERROR)


class EntityNotFoundError(ResourceNotFoundError):
    """
    Error que se produce cuando una entidad solicitada no se encuentra.
    """

    def __init__(
        self,
        message: str,
        entity_id: Any | None = None,
        entity_type: str | None = None,
        context: dict[str, Any] | None = None,
    ):
        """
        Inicializa un nuevo error de entidad no encontrada.

        Args:
            message: Mensaje descriptivo del error.
            entity_id: Identificador opcional de la entidad no encontrada.
            entity_type: Tipo opcional de la entidad no encontrada.
            context: Diccionario opcional con información de contexto adicional.
        """
        super().__init__(message, resource_id=entity_id, resource_type=entity_type, context=context)


class DuplicateEntityError(DomainError):
    """
    Error que se produce cuando se intenta crear una entidad que ya existe.
    """

    def __init__(
        self,
        message: str,
        entity_id: Any | None = None,
        entity_type: str | None = None,
        context: dict[str, Any] | None = None,
    ):
        """
        Inicializa un nuevo error de entidad duplicada.

        Args:
            message: Mensaje descriptivo del error.
            entity_id: Identificador opcional de la entidad duplicada.
            entity_type: Tipo opcional de la entidad duplicada.
            context: Diccionario opcional con información de contexto adicional.
        """
        ctx = context or {}
        if entity_id is not None:
            ctx["entity_id"] = str(entity_id)
        if entity_type is not None:
            ctx["entity_type"] = entity_type

        super().__init__(message, ctx, logging.WARNING)
