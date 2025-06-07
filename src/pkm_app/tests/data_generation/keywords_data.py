"""
Module for generating keyword (tag) test data
"""

import uuid
from datetime import datetime, UTC
from faker import Faker
from src.pkm_app.core.domain.entities.keyword import Keyword

fake = Faker()


def generate_keywords(users, min_per_user=3, max_per_user=5):
    """
    Generate test keywords for given users
    Returns list of Keyword entities
    """
    keywords = []
    for user in users:
        num_keywords = fake.random_int(min=min_per_user, max=max_per_user)

        for _ in range(num_keywords):
            keyword = Keyword(
                id=uuid.uuid4(),
                name=fake.word(),
                user_id=user.id,
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            )
            keywords.append(keyword)
    return keywords
