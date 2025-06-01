"""Create User Profile Use Case."""

import logging
from typing import Optional
from uuid import uuid4

from pkm_app.core.application.dtos.user_profile_dto import UserProfileDTO
from pkm_app.core.application.interfaces.unit_of_work_interface import IUnitOfWork
from pkm_app.core.application.interfaces.user_profile_interface import IUserProfileRepository
from pkm_app.core.domain.entities.user_profile import UserProfile

# Configure logger for this module
logger = logging.getLogger(__name__)


class CreateUserProfileUseCase:
    """
    Use case for creating a new user profile.

    This use case handles the business logic required to create a new user profile
    within the system. It interacts with the repository to persist the new profile
    and ensures that all necessary operations are performed within a unit of work.
    """

    def __init__(self, user_profile_repository: IUserProfileRepository, unit_of_work: IUnitOfWork):
        """
        Initialize the CreateUserProfileUseCase.

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
            "CreateUserProfileUseCase initialized with repository: %s and unit_of_work: %s",
            user_profile_repository.__class__.__name__,
            unit_of_work.__class__.__name__,
        )

    async def execute(self, user_profile_data: UserProfileDTO) -> UserProfileDTO | None:
        """
        Execute the use case to create a new user profile.

        Args:
            user_profile_data: Data Transfer Object containing the details for the new user profile.

        Returns:
            A DTO representing the created user profile, or None if creation failed.

        Raises:
            ValueError: If user_profile_data is invalid.
            Exception: For any other errors during the creation process.
        """
        logger.info("Executing CreateUserProfileUseCase with data: %s", user_profile_data)

        if not isinstance(user_profile_data, UserProfileDTO):
            logger.warning("Invalid user_profile_data type: %s", type(user_profile_data).__name__)
            raise ValueError("user_profile_data must be a UserProfileDTO instance.")

        try:
            # Configurar el contexto asíncrono manualmente
            await self.unit_of_work.begin()
            try:
                # Generate a new ID if not provided
                profile_id = user_profile_data.id if user_profile_data.id else uuid4()

                # Create new profile with all required fields
                profile_data = {
                    "id": profile_id,
                    "username": user_profile_data.username,
                    "email": user_profile_data.email,
                }
                new_user_profile = UserProfile(**profile_data)
                logger.debug("Creating UserProfile entity: %s", new_user_profile)

                await self.user_profile_repository.add(new_user_profile)
                await self.unit_of_work.commit()

                logger.info("Successfully created user profile with ID: %s", new_user_profile.id)
                return UserProfileDTO.from_entity(new_user_profile)
            except Exception:
                await self.unit_of_work.rollback()
                raise

        except ValueError as ve:
            logger.error("ValueError during user profile creation: %s", ve, exc_info=True)
            await self.unit_of_work.rollback()
            raise
        except Exception as e:
            logger.error(
                "An unexpected error occurred during user profile creation: %s", e, exc_info=True
            )
            await self.unit_of_work.rollback()
            # Consider re-raising a more specific application-level exception
            raise Exception(f"Failed to create user profile: {e}") from e
