"""Seed data migration

Revision ID: 20250602_201844
Revises: e9e6a35c39f1
Create Date: 2025-06-02T20:18:44.526128

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20250602_201844"
down_revision = "e9e6a35c39f1"
branch_labels = None
depends_on = None


def upgrade():
    # Read seed data SQL
    with open("src/pkm_app/infrastructure/persistence/schema/seed.sql") as f:
        sql = f.read()
        op.execute(sql)


def downgrade():
    # Remove all seed data
    op.execute("DELETE FROM note_keywords;")
    op.execute("DELETE FROM note_links;")
    op.execute("DELETE FROM notes;")
    op.execute("DELETE FROM keywords;")
    op.execute("DELETE FROM sources;")
    op.execute("DELETE FROM projects;")
    op.execute("DELETE FROM user_profiles;")
