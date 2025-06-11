"""
Module for generating note test data
"""

import uuid
from datetime import datetime, UTC
from faker import Faker
import random
from src.pkm_app.core.domain.entities.note import Note

fake = Faker()
note_types = ["markdown", "text", "code", "mixed"]


def generate_notes(users, projects, sources, keywords, min_per_project=3, max_per_project=5):
    """
    Generate test notes with relationships to users, projects, sources, and keywords
    Returns list of Note entities
    """
    notes = []

    # For each project, generate notes
    for project in projects:
        # Find the owner of this project from metadata
        owner_id = project.metadata.get("owner_id")
        if not owner_id:
            continue
        owner = next((u for u in users if str(u.id) == owner_id), None)
        if not owner:
            continue

        # Get sources and keywords for this owner
        owner_sources = [s for s in sources if s.metadata.get("user_id") == str(owner.id)]
        owner_keywords = [k for k in keywords if k.user_id == owner.id]

        num_notes = random.randint(min_per_project, max_per_project)

        for _ in range(num_notes):
            note_type = random.choice(note_types)
            source = random.choice(owner_sources) if owner_sources else None
            note_keywords = (
                random.sample(owner_keywords, min(2, len(owner_keywords))) if owner_keywords else []
            )

            note = Note(
                id=uuid.uuid4(),
                title=f"Note: {fake.sentence(nb_words=4)}",
                content=fake.paragraph(nb_sentences=5),
                type=note_type,
                metadata={"tags": [kw.name for kw in note_keywords], "user_id": str(owner.id)},
                project_id=project.id,
                source_id=source.id if source else None,
                keyword_ids=[kw.id for kw in note_keywords],
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            )
            notes.append(note)
    return notes
