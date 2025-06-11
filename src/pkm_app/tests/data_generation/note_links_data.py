"""
Module for generating note link test data
"""

import uuid
import random
from datetime import datetime, UTC
from src.pkm_app.core.domain.entities.note_link import NoteLink


def generate_note_links(notes, min_per_note=1, max_per_note=2):
    """
    Generate note links between existing notes
    Returns list of NoteLink entities
    """
    note_links = []

    for note in notes:
        # Avoid linking a note to itself
        other_notes = [n for n in notes if n.id != note.id]
        if not other_notes:
            continue

        num_links = random.randint(min_per_note, max_per_note)
        linked_notes = random.sample(other_notes, min(num_links, len(other_notes)))

        for target_note in linked_notes:
            note_link = NoteLink(
                id=uuid.uuid4(),
                source_note_id=note.id,
                target_note_id=target_note.id,
                link_type=random.choice(
                    ["reference", "relates_to", "depends_on", "contradicts", "supports"]
                ),
                metadata={},
                created_at=note.created_at,  # Use same timestamp as source note
                updated_at=note.updated_at,
            )
            note_links.append(note_link)
    return note_links
