"""List User Profiles Use Case."""

import logging
from typing import Any, Optional

from pkm_app.core.application.dtos.user_profile_dto import UserProfileDTO
from pkm_app.core.application.interfaces.user_profile_interface import IUserProfileRepository

# Configure logger for this module
logger = logging.getLogger(__name__)


class ListUserProfilesUseCase:
    """
    Use case for listing all user profiles.

    This use case handles the business logic required to retrieve a list of all
    user profiles currently stored in the system. It can also handle
    optional filtering, pagination, and sorting if implemented in the repository.
    """

    def __init__(self, user_profile_repository: IUserProfileRepository):
        """
        Initialize the ListUserProfilesUseCase.

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
            "ListUserProfilesUseCase initialized with repository: %s",
            user_profile_repository.__class__.__name__,
        )

    async def execute(
        self, filters: dict[str, Any] | None = None, offset: int = 0, limit: int = 100
    ) -> list[UserProfileDTO]:
        """
        Execute the use case to list user profiles.

        Args:
            filters: Optional dictionary of filters to apply.
                     Example: {"username_contains": "john"}
            offset: Optional offset for pagination.
            limit: Optional limit for pagination.

        Returns:
            A list of DTOs representing the user profiles.

        Raises:
            Exception: For any errors during the listing process.
        """
        logger.info(
            "Executing ListUserProfilesUseCase with filters: %s, offset: %d, limit: %d",
            filters,
            offset,
            limit,
        )

        try:
            # The list_all method in the repository should handle pagination and filtering
            user_profiles = await self.user_profile_repository.list_all(
                filters=filters, offset=offset, limit=limit
            )

            if not user_profiles:
                logger.info("No user profiles found matching the criteria.")
                return []

            logger.info("Successfully retrieved %d user profiles.", len(user_profiles))
            return [UserProfileDTO.from_entity(profile) for profile in user_profiles]

        except Exception as e:
            logger.error(
                "An unexpected error occurred while listing user profiles: %s", e, exc_info=True
            )
            # Consider re-raising a more specific application-level exception
            raise Exception(f"Failed to list user profiles: {e}") from e
