"""initial_migration_setup

Revision ID: e9e6a35c39f1
Revises:
Create Date: 2025-05-26 21:11:42.809360

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "e9e6a35c39f1"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "user_profiles",
        sa.Column("user_id", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=True),
        sa.Column("email", sa.Text(), nullable=True),
        sa.Column("preferences", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("learned_context", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("user_id", name=op.f("pk_user_profiles")),
    )
    op.create_index(op.f("ix_user_profiles_email"), "user_profiles", ["email"], unique=True)
    op.create_table(
        "keywords",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user_profiles.user_id"],
            name=op.f("fk_keywords_user_id_user_profiles"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_keywords")),
        sa.UniqueConstraint("user_id", "name", name="uq_keywords_user_id_name"),
    )
    op.create_index(op.f("ix_keywords_name"), "keywords", ["name"], unique=False)
    op.create_table(
        "projects",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("parent_project_id", sa.UUID(), nullable=True),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["parent_project_id"],
            ["projects.id"],
            name=op.f("fk_projects_parent_project_id_projects"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user_profiles.user_id"],
            name=op.f("fk_projects_user_id_user_profiles"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_projects")),
    )
    op.create_index(op.f("ix_projects_name"), "projects", ["name"], unique=False)
    op.create_index(
        op.f("ix_projects_parent_project_id"), "projects", ["parent_project_id"], unique=False
    )
    op.create_index(op.f("ix_projects_user_id"), "projects", ["user_id"], unique=False)
    op.create_table(
        "sources",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.Text(), nullable=False),
        sa.Column("type", sa.VARCHAR(length=100), nullable=True),
        sa.Column("title", sa.Text(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("url", sa.Text(), nullable=True),
        sa.Column("link_metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user_profiles.user_id"],
            name=op.f("fk_sources_user_id_user_profiles"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_sources")),
    )
    op.create_index(op.f("ix_sources_title"), "sources", ["title"], unique=False)
    op.create_index(op.f("ix_sources_type"), "sources", ["type"], unique=False)
    op.create_index(op.f("ix_sources_url"), "sources", ["url"], unique=False)
    op.create_index(op.f("ix_sources_user_id"), "sources", ["user_id"], unique=False)
    op.create_table(
        "notes",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.Text(), nullable=False),
        sa.Column("project_id", sa.UUID(), nullable=True),
        sa.Column("source_id", sa.UUID(), nullable=True),
        sa.Column("title", sa.Text(), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("type", sa.VARCHAR(length=100), nullable=True),
        sa.Column("note_metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
            name=op.f("fk_notes_project_id_projects"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["source_id"],
            ["sources.id"],
            name=op.f("fk_notes_source_id_sources"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user_profiles.user_id"],
            name=op.f("fk_notes_user_id_user_profiles"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_notes")),
    )
    op.create_index(op.f("ix_notes_created_at"), "notes", ["created_at"], unique=False)
    op.create_index(op.f("ix_notes_project_id"), "notes", ["project_id"], unique=False)
    op.create_index(op.f("ix_notes_source_id"), "notes", ["source_id"], unique=False)
    op.create_index(op.f("ix_notes_title"), "notes", ["title"], unique=False)
    op.create_index(op.f("ix_notes_type"), "notes", ["type"], unique=False)
    op.create_index(op.f("ix_notes_updated_at"), "notes", ["updated_at"], unique=False)
    op.create_index(op.f("ix_notes_user_id"), "notes", ["user_id"], unique=False)
    op.create_table(
        "note_keywords",
        sa.Column("note_id", sa.UUID(), nullable=False),
        sa.Column("keyword_id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["keyword_id"],
            ["keywords.id"],
            name=op.f("fk_note_keywords_keyword_id_keywords"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["note_id"],
            ["notes.id"],
            name=op.f("fk_note_keywords_note_id_notes"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("note_id", "keyword_id", name=op.f("pk_note_keywords")),
    )
    op.create_index("idx_note_keywords_keyword_id", "note_keywords", ["keyword_id"], unique=False)
    op.create_index("idx_note_keywords_note_id", "note_keywords", ["note_id"], unique=False)
    op.create_table(
        "note_links",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("source_note_id", sa.UUID(), nullable=False),
        sa.Column("target_note_id", sa.UUID(), nullable=False),
        sa.Column("link_type", sa.VARCHAR(length=100), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("user_id", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "source_note_id <> target_note_id",
            name=op.f("ck_note_links_ck_note_links_different_notes"),
        ),
        sa.ForeignKeyConstraint(
            ["source_note_id"],
            ["notes.id"],
            name=op.f("fk_note_links_source_note_id_notes"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["target_note_id"],
            ["notes.id"],
            name=op.f("fk_note_links_target_note_id_notes"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user_profiles.user_id"],
            name=op.f("fk_note_links_user_id_user_profiles"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_note_links")),
        sa.UniqueConstraint(
            "source_note_id",
            "target_note_id",
            "user_id",
            "link_type",
            name="uq_note_links_source_target_user_type",
        ),
    )
    op.create_index(op.f("ix_note_links_link_type"), "note_links", ["link_type"], unique=False)
    op.create_index(
        op.f("ix_note_links_source_note_id"), "note_links", ["source_note_id"], unique=False
    )
    op.create_index(
        op.f("ix_note_links_target_note_id"), "note_links", ["target_note_id"], unique=False
    )
    op.create_index(op.f("ix_note_links_user_id"), "note_links", ["user_id"], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_note_links_user_id"), table_name="note_links")
    op.drop_index(op.f("ix_note_links_target_note_id"), table_name="note_links")
    op.drop_index(op.f("ix_note_links_source_note_id"), table_name="note_links")
    op.drop_index(op.f("ix_note_links_link_type"), table_name="note_links")
    op.drop_table("note_links")
    op.drop_index("idx_note_keywords_note_id", table_name="note_keywords")
    op.drop_index("idx_note_keywords_keyword_id", table_name="note_keywords")
    op.drop_table("note_keywords")
    op.drop_index(op.f("ix_notes_user_id"), table_name="notes")
    op.drop_index(op.f("ix_notes_updated_at"), table_name="notes")
    op.drop_index(op.f("ix_notes_type"), table_name="notes")
    op.drop_index(op.f("ix_notes_title"), table_name="notes")
    op.drop_index(op.f("ix_notes_source_id"), table_name="notes")
    op.drop_index(op.f("ix_notes_project_id"), table_name="notes")
    op.drop_index(op.f("ix_notes_created_at"), table_name="notes")
    op.drop_table("notes")
    op.drop_index(op.f("ix_sources_user_id"), table_name="sources")
    op.drop_index(op.f("ix_sources_url"), table_name="sources")
    op.drop_index(op.f("ix_sources_type"), table_name="sources")
    op.drop_index(op.f("ix_sources_title"), table_name="sources")
    op.drop_table("sources")
    op.drop_index(op.f("ix_projects_user_id"), table_name="projects")
    op.drop_index(op.f("ix_projects_parent_project_id"), table_name="projects")
    op.drop_index(op.f("ix_projects_name"), table_name="projects")
    op.drop_table("projects")
    op.drop_index(op.f("ix_keywords_name"), table_name="keywords")
    op.drop_table("keywords")
    op.drop_index(op.f("ix_user_profiles_email"), table_name="user_profiles")
    op.drop_table("user_profiles")
    # ### end Alembic commands ###
