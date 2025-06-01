from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import Text
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from .base import Base

if TYPE_CHECKING:
    from .keyword import Keyword
    from .note import Note
    from .project import Project
    from .source import Source

    # from .template import Template # If Template model is created


class UserProfile(Base):
    __tablename__ = "user_profiles"

    user_id: Mapped[str] = mapped_column(Text, primary_key=True)
    name: Mapped[str | None] = mapped_column(Text, nullable=True)
    email: Mapped[str | None] = mapped_column(Text, unique=True, nullable=True, index=True)
    preferences: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    learned_context: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relaciones (hacia abajo)
    projects: Mapped[list[Project]] = relationship(back_populates="user")
    sources: Mapped[list[Source]] = relationship(back_populates="user")
    notes: Mapped[list[Note]] = relationship(back_populates="user")
    keywords: Mapped[list[Keyword]] = relationship(back_populates="user")
    # templates: Mapped[List["Template"]] = relationship(back_populates="user")

    def __repr__(self) -> str:
        return f"<UserProfile(user_id='{self.user_id}', name='{self.name}')>"
