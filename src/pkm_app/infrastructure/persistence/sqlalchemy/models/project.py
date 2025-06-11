from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Text
from sqlalchemy.dialects.postgresql import TIMESTAMP, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from .base import Base, generate_uuid

if TYPE_CHECKING:
    from .note import Note
    from .user_profile import UserProfile

    # from .project_template import ProjectTemplate


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=generate_uuid
    )
    user_id: Mapped[str] = mapped_column(
        Text,
        ForeignKey("user_profiles.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    parent_project_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relaciones
    user: Mapped[UserProfile] = relationship(back_populates="projects")
    notes: Mapped[list[Note]] = relationship(back_populates="project")

    parent_project: Mapped[Project | None] = relationship(
        back_populates="child_projects", remote_side=[id]
    )
    child_projects: Mapped[list[Project]] = relationship(
        back_populates="parent_project", cascade="all, delete-orphan"
    )
    # templates_associated: Mapped[List["ProjectTemplate"]] =
    # relationship(back_populates="project", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Project(id='{self.id}', name='{self.name}')>"
