from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import TIMESTAMP, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from .associations import note_keywords_association_table
from .base import Base, generate_uuid

if TYPE_CHECKING:
    from .note import Note
    from .user_profile import UserProfile


class Keyword(Base):
    __tablename__ = "keywords"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=generate_uuid
    )
    user_id: Mapped[str] = mapped_column(
        Text, ForeignKey("user_profiles.user_id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (UniqueConstraint("user_id", "name", name="uq_keywords_user_id_name"),)

    # Relaciones
    user: Mapped[UserProfile] = relationship(back_populates="keywords")
    notes: Mapped[list[Note]] = relationship(
        secondary=note_keywords_association_table, back_populates="keywords"
    )

    def __repr__(self) -> str:
        return f"<Keyword(id='{self.id}', name='{self.name}')>"
