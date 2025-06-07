"""
Module for generating user profile test data
"""

import uuid
from datetime import datetime, UTC
from faker import Faker
from src.pkm_app.core.domain.entities.user_profile import UserProfile

fake = Faker()


def generate_user_profiles(count=2):
    """
    Generate test user profiles
    Returns list of UserProfile entities
    """
    users = []
    for _ in range(count):
        user = UserProfile(
            id=uuid.uuid4(),
            username=fake.user_name(),
            email=fake.email(),
            display_name=fake.name(),
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            preferences={"theme": "dark", "language": "es"},
        )
        users.append(user)
    return users
