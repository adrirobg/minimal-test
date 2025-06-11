from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP, UUID, VARCHAR

# Descomenta la siguiente línea cuando vayas a implementar embeddings
# from pgvector.sqlalchemy import Vector
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from .associations import note_keywords_association_table
from .base import Base, generate_uuid

if TYPE_CHECKING:
    from .keyword import Keyword
    from .note_link import NoteLink
    from .project import Project
    from .source import Source
    from .user_profile import UserProfile

    # from .embedding import Embedding # If Embedding model is created


class Note(Base):
    __tablename__ = "notes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=generate_uuid
    )
    user_id: Mapped[str] = mapped_column(
        Text,
        ForeignKey("user_profiles.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    project_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    source_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sources.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    title: Mapped[str | None] = mapped_column(Text, nullable=True, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[str | None] = mapped_column(VARCHAR(100), nullable=True, index=True)
    # embedding: Mapped[Optional[list[float]]] =
    # mapped_column(Vector(768), nullable=True)
    note_metadata: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False, index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        index=True,
    )

    # Relaciones
    user: Mapped[UserProfile] = relationship(back_populates="notes")
    project: Mapped[Project | None] = relationship(back_populates="notes")
    source: Mapped[Source | None] = relationship(back_populates="notes")

    keywords: Mapped[list[Keyword]] = relationship(
        secondary=note_keywords_association_table, back_populates="notes"
    )

    source_of_links: Mapped[list[NoteLink]] = relationship(
        foreign_keys="NoteLink.source_note_id",
        back_populates="source_note",
        cascade="all, delete-orphan",
    )
    target_of_links: Mapped[list[NoteLink]] = relationship(
        foreign_keys="NoteLink.target_note_id",
        back_populates="target_note",
        cascade="all, delete-orphan",
    )

    # embeddings_rel: Mapped[List["Embedding"]] =
    # relationship(back_populates="note", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Note(id='{self.id}', title='{self.title}')>"
