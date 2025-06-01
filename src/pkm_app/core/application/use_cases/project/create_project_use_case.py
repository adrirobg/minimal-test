import logging
import uuid
from datetime import datetime

from src.pkm_app.core.application.dtos import ProjectCreate, ProjectSchema
from src.pkm_app.core.application.interfaces.project_interface import IProjectRepository
from src.pkm_app.core.application.interfaces.unit_of_work_interface import (
    IUnitOfWork,
)
from src.pkm_app.core.domain.errors import PermissionDeniedError, RepositoryError, ValidationError

# Configurar logger para este caso de uso
logger = logging.getLogger(__name__)


class CreateProjectUseCase:
    """
    Caso de uso para crear un nuevo proyecto.
    Sigue el patrón de user_profile: inyección explícita de repositorio y unit_of_work, logging robusto y uso de DTOs.
    """

    def __init__(self, project_repository: IProjectRepository, unit_of_work: IUnitOfWork) -> None:
        """
        Inicializa el caso de uso de creación de proyecto.

        Args:
            project_repository: Repositorio de proyectos (IProjectRepository).
            unit_of_work: Unidad de trabajo para transacciones.
        """
        self.project_repository = project_repository
        self.unit_of_work = unit_of_work
        logger.info(
            "CreateProjectUseCase inicializado con repositorio: %s y unit_of_work: %s",
            project_repository.__class__.__name__,
            unit_of_work.__class__.__name__,
        )

    async def execute(self, user_id: str) -> ProjectSchema:
        """
        Crea un nuevo proyecto.

        Args:
            user_id: ID del usuario que crea el proyecto.

        Returns:
            El proyecto creado.

        Raises:
            ValidationError: Si los datos de entrada son inválidos.
            PermissionDeniedError: Si el usuario no tiene permisos.
            RepositoryError: Si ocurre un error en la capa de persistencia.
        """
        logger.info(
            "Operación iniciada: Crear proyecto",
            extra={"user_id": user_id, "operation": "create_project"},
        )

        if not user_id:
            logger.warning(
                "Intento de creación de proyecto sin user_id.",
                extra={"operation": "create_project"},
            )
            raise PermissionDeniedError("Se requiere ID de usuario para crear un proyecto")

        # TODO: Implementar la lógica para crear un proyecto
        # Placeholder para satisfacer el type checker
        return ProjectSchema(
            id=uuid.uuid4(),
            name="Proyecto de prueba",
            description="Descripción de prueba",
            user_id=user_id,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
