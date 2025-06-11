"""Delete User Profile Use Case."""

import logging
from uuid import UUID

from pkm_app.core.application.interfaces.unit_of_work_interface import IUnitOfWork
from pkm_app.core.application.interfaces.user_profile_interface import IUserProfileRepository
from pkm_app.core.domain.errors import EntityNotFoundError

# Configure logger for this module
logger = logging.getLogger(__name__)


class DeleteUserProfileUseCase:
    """
    Use case for deleting an existing user profile.

    This use case handles the business logic required to remove a user profile
    from the system. It ensures that the operation is performed atomically and
    that the profile exists before attempting deletion.
    """

    def __init__(self, user_profile_repository: IUserProfileRepository, unit_of_work: IUnitOfWork):
        """
        Initialize the DeleteUserProfileUseCase.

        Args:
            user_profile_repository: The repository for user profile data access.
            unit_of_work: The unit of work for managing transactions.
        """
        if not isinstance(user_profile_repository, IUserProfileRepository):
            logger.error(
                "Invalid user_profile_repository instance: %s",
                type(user_profile_repository).__name__,
            )
            raise TypeError("user_profile_repository must be an instance of IUserProfileRepository")
        if not isinstance(unit_of_work, IUnitOfWork):
            logger.error("Invalid unit_of_work instance: %s", type(unit_of_work).__name__)
            raise TypeError("unit_of_work must be an instance of IUnitOfWork")

        self.user_profile_repository = user_profile_repository
        self.unit_of_work = unit_of_work
        logger.info(
            "DeleteUserProfileUseCase initialized with repository: %s and unit_of_work: %s",
            user_profile_repository.__class__.__name__,
            unit_of_work.__class__.__name__,
        )

    async def execute(self, user_profile_id: UUID) -> bool:
        """
        Execute the use case to delete an existing user profile.

        Args:
            user_profile_id: The ID of the user profile to delete.

        Returns:
            True if the user profile was successfully deleted, False otherwise.

        Raises:
            ValueError: If user_profile_id is not a valid UUID.
            EntityNotFoundError: If the user profile with the given ID does not exist.
            Exception: For any other errors during the deletion process.
        """
        logger.info("Executing DeleteUserProfileUseCase for user_profile_id: %s", user_profile_id)

        if not isinstance(user_profile_id, UUID):
            logger.warning(
                "Invalid user_profile_id type: %s. Must be UUID.", type(user_profile_id).__name__
            )
            raise ValueError("user_profile_id must be a valid UUID.")

        try:
            # Configurar el contexto asíncrono manualmente
            await self.unit_of_work.begin()
            try:
                # Verificar existencia usando exists() en lugar de get_by_id()
                exists = await self.user_profile_repository.exists(user_profile_id)

                if not exists:
                    logger.warning(
                        "User profile with ID %s not found for deletion.", user_profile_id
                    )
                    await self.unit_of_work.rollback()
                    raise EntityNotFoundError(
                        f"User profile with ID '{user_profile_id}' not found."
                    )

                logger.debug(
                    "User profile with ID %s exists. Proceeding with deletion.", user_profile_id
                )
                await self.user_profile_repository.delete(user_profile_id)
                await self.unit_of_work.commit()
                logger.info("Successfully deleted user profile with ID: %s", user_profile_id)
                return True
            except Exception:
                await self.unit_of_work.rollback()
                raise

        except EntityNotFoundError:
            # Rollback ya fue llamado en el bloque anterior
            raise
        except ValueError as ve:  # Catches the ValueError from the ID check
            logger.error(
                "ValueError during user profile deletion for ID %s: %s",
                user_profile_id,
                ve,
                exc_info=True,
            )
            await self.unit_of_work.rollback()  # Ensure rollback on validation error too
            raise
        except Exception as e:
            logger.error(
                "An unexpected error occurred during user profile deletion for ID %s: %s",
                user_profile_id,
                e,
                exc_info=True,
            )
            await self.unit_of_work.rollback()
            # Consider re-raising a more specific application-level exception
            raise Exception(f"Failed to delete user profile {user_profile_id}: {e}") from e
