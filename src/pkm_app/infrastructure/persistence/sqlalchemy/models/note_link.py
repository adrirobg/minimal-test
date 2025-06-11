from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import TIMESTAMP, UUID, VARCHAR
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from .base import Base, generate_uuid

if TYPE_CHECKING:
    from .note import Note
    from .user_profile import UserProfile


class NoteLink(Base):
    __tablename__ = "note_links"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=generate_uuid
    )
    source_note_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("notes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    target_note_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("notes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    link_type: Mapped[str | None] = mapped_column(
        VARCHAR(100), default="related", nullable=True, index=True
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    user_id: Mapped[str] = mapped_column(
        Text,
        ForeignKey("user_profiles.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        UniqueConstraint(
            "source_note_id",
            "target_note_id",
            "user_id",
            "link_type",
            name="uq_note_links_source_target_user_type",
        ),
        CheckConstraint("source_note_id <> target_note_id", name="ck_note_links_different_notes"),
    )

    # Relaciones
    user: Mapped[UserProfile] = (
        relationship()
    )  # No back_populates needed if UserProfile doesn't list NoteLinks

    source_note: Mapped[Note] = relationship(
        foreign_keys=[source_note_id], back_populates="source_of_links"
    )
    target_note: Mapped[Note] = relationship(
        foreign_keys=[target_note_id], back_populates="target_of_links"
    )

    def __repr__(self) -> str:
        return (
            f"<NoteLink(id='{self.id}', source='{self.source_note_id}', "
            f"target='{self.target_note_id}', type='{self.link_type}')>"
        )
