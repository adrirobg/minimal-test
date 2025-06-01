from __future__ import annotations

from sqlalchemy import Column, ForeignKey, Index, Table
from sqlalchemy.dialects.postgresql import UUID

from .base import Base

note_keywords_association_table = Table(
    "note_keywords",
    Base.metadata,
    Column(
        "note_id",
        UUID(as_uuid=True),
        ForeignKey("notes.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "keyword_id",
        UUID(as_uuid=True),
        ForeignKey("keywords.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Index("idx_note_keywords_note_id", "note_id"),
    Index("idx_note_keywords_keyword_id", "keyword_id"),
)
