"""Update User Profile Use Case."""

import logging
from typing import Any, Dict, Optional
from uuid import UUID

from pkm_app.core.application.dtos.user_profile_dto import UserProfileDTO
from pkm_app.core.application.interfaces.unit_of_work_interface import IUnitOfWork
from pkm_app.core.application.interfaces.user_profile_interface import IUserProfileRepository
from pkm_app.core.domain.entities.user_profile import UserProfile
from pkm_app.core.domain.errors import DuplicateEntityError, EntityNotFoundError

# Configure logger for this module
logger = logging.getLogger(__name__)


class UpdateUserProfileUseCase:
    """
    Use case for updating an existing user profile.

    This use case handles the business logic required to modify an existing
    user profile in the system. It ensures that updates are performed
    atomically and that the profile exists before attempting an update.
    """

    def __init__(self, user_profile_repository: IUserProfileRepository, unit_of_work: IUnitOfWork):
        """
        Initialize the UpdateUserProfileUseCase.

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
            "UpdateUserProfileUseCase initialized with repository: %s and unit_of_work: %s",
            user_profile_repository.__class__.__name__,
            unit_of_work.__class__.__name__,
        )

    async def execute(
        self, user_profile_id: UUID, update_data: dict[str, Any]
    ) -> UserProfileDTO | None:
        """
        Execute the use case to update an existing user profile.

        Args:
            user_profile_id: The ID of the user profile to update.
            update_data: A dictionary containing the fields to update and their new values.
                         Example: {"username": "new_username", "email": "new_email@example.com"}

        Returns:
            A DTO representing the updated user profile, or None if the update failed
            or the profile was not found.

        Raises:
            ValueError: If user_profile_id is not a valid UUID or update_data is empty.
            EntityNotFoundError: If the user profile with the given ID does not exist.
            Exception: For any other errors during the update process.
        """
        logger.info(
            "Executing UpdateUserProfileUseCase for user_profile_id: %s with data: %s",
            user_profile_id,
            update_data,
        )

        if not isinstance(user_profile_id, UUID):
            logger.warning(
                "Invalid user_profile_id type: %s. Must be UUID.", type(user_profile_id).__name__
            )
            raise ValueError("user_profile_id must be a valid UUID.")
        if not update_data:
            logger.warning(
                "update_data is empty. No fields to update for user_profile_id: %s", user_profile_id
            )
            raise ValueError("update_data cannot be empty.")

        try:
            # Configurar el contexto asíncrono manualmente
            await self.unit_of_work.begin()
            user_profile = await self.user_profile_repository.get_by_id(user_profile_id)

            if user_profile is None:
                logger.warning("User profile with ID %s not found for update.", user_profile_id)
                raise EntityNotFoundError(f"User profile with ID '{user_profile_id}' not found.")

            logger.debug("User profile found: %s. Applying updates: %s", user_profile, update_data)

            # Create a new entity with updated values (since UserProfile is frozen)
            update_dict = user_profile.model_dump()
            for field, value in update_data.items():
                if field in update_dict:
                    update_dict[field] = value
                else:
                    logger.warning(
                        "Field '%s' does not exist on UserProfile entity. Skipping update for this field.",
                        field,
                    )

            updated_profile = UserProfile(**update_dict)
            await self.user_profile_repository.update(updated_profile)
            await self.unit_of_work.commit()

            logger.info("Successfully updated user profile with ID: %s", user_profile_id)
            return UserProfileDTO.from_entity(updated_profile)

        except EntityNotFoundError as e:
            logger.warning(str(e))
            await self.unit_of_work.rollback()
            raise
        except DuplicateEntityError as e:
            logger.warning(str(e))
            await self.unit_of_work.rollback()
            raise
        except Exception as e:
            logger.error(
                "An unexpected error occurred during user profile update for ID %s: %s",
                user_profile_id,
                e,
                exc_info=True,
            )
            await self.unit_of_work.rollback()
            raise Exception(f"Failed to update user profile {user_profile_id}: {e}") from e
