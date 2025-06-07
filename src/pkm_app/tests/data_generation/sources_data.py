"""
Module for generating source test data
"""

import uuid
from datetime import datetime, UTC
from faker import Faker
from src.pkm_app.core.domain.entities.source import Source

fake = Faker()


def generate_sources(users, min_per_user=1, max_per_user=2):
    """
    Generate test sources for given users
    Returns list of Source entities
    """
    sources = []
    source_types = ["article", "book", "website", "video"]  # Using valid types from entity

    for user in users:
        num_sources = fake.random_int(min=min_per_user, max=max_per_user)

        for _ in range(num_sources):
            source_type = fake.random_element(elements=source_types)
            source = Source(
                id=uuid.uuid4(),
                title=f"{source_type.capitalize()}: {fake.sentence(nb_words=3)}",
                source_type=source_type,
                url=fake.url() if source_type in ["website", "video"] else None,
                metadata={"user_id": str(user.id), "description": fake.paragraph()},
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            )
            sources.append(source)
    return sources
