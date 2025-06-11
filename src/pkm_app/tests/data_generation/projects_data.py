"""
Module for generating project test data
"""

import uuid
from datetime import datetime, UTC
from faker import Faker
from src.pkm_app.core.domain.entities.project import Project

fake = Faker()


def generate_projects(users, min_per_user=2, max_per_user=3):
    """
    Generate test projects for given users
    Returns list of Project entities
    """
    projects = []
    for user in users:
        # Determine number of projects for this user
        num_projects = fake.random_int(min=min_per_user, max=max_per_user)

        for i in range(num_projects):
            project = Project(
                id=uuid.uuid4(),
                name=f"Project {fake.word().capitalize()}",
                description=fake.sentence(),
                status="active",
                metadata={"owner_id": str(user.id)},
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            )
            projects.append(project)
    return projects
