"""Get User Profile Use Case."""

import logging
from typing import Optional
from uuid import UUID

from pkm_app.core.application.dtos.user_profile_dto import UserProfileDTO
from pkm_app.core.application.interfaces.user_profile_interface import IUserProfileRepository
from pkm_app.core.domain.errors import EntityNotFoundError

# Configure logger for this module
logger = logging.getLogger(__name__)


class GetUserProfileUseCase:
    """
    Use case for retrieving a specific user profile by its ID.

    This use case handles the business logic required to fetch a user profile
    from the system using its unique identifier.
    """

    def __init__(self, user_profile_repository: IUserProfileRepository):
        """
        Initialize the GetUserProfileUseCase.

        Args:
            user_profile_repository: The repository for user profile data access.
        """
        if not isinstance(user_profile_repository, IUserProfileRepository):
            logger.error(
                "Invalid user_profile_repository instance: %s",
                type(user_profile_repository).__name__,
            )
            raise TypeError("user_profile_repository must be an instance of IUserProfileRepository")

        self.user_profile_repository = user_profile_repository
        logger.info(
            "GetUserProfileUseCase initialized with repository: %s",
            user_profile_repository.__class__.__name__,
        )

    async def execute(self, user_profile_id: UUID) -> UserProfileDTO | None:
        """
        Execute the use case to retrieve a user profile.

        Args:
            user_profile_id: The unique identifier of the user profile to retrieve.

        Returns:
            A DTO representing the found user profile, or None if not found.

        Raises:
            ValueError: If user_profile_id is not a valid UUID.
            EntityNotFoundError: If the user profile with the given ID does not exist.
            Exception: For any other errors during the retrieval process.
        """
        logger.info("Executing GetUserProfileUseCase for user_profile_id: %s", user_profile_id)

        if not isinstance(user_profile_id, UUID):
            logger.warning(
                "Invalid user_profile_id type: %s. Must be UUID.", type(user_profile_id).__name__
            )
            raise ValueError("user_profile_id must be a valid UUID.")

        try:
            user_profile = await self.user_profile_repository.get_by_id(user_profile_id)

            if user_profile is None:
                logger.warning("User profile with ID %s not found.", user_profile_id)
                raise EntityNotFoundError(f"User profile with ID '{user_profile_id}' not found.")

            logger.info("Successfully retrieved user profile with ID: %s", user_profile_id)
            return UserProfileDTO.from_entity(user_profile)

        except EntityNotFoundError:
            # Re-raise EntityNotFoundError to be handled by the caller
            raise
        except Exception as e:
            logger.error(
                "An unexpected error occurred while retrieving user profile %s: %s",
                user_profile_id,
                e,
                exc_info=True,
            )
            # Consider re-raising a more specific application-level exception
            raise Exception(f"Failed to retrieve user profile {user_profile_id}: {e}") from e
