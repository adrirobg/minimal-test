"""
Main module for generating test data for the PKM application.
This script coordinates the generation of all test data entities and SQL files.
"""

import uuid
import os
from datetime import datetime
from src.pkm_app.tests.data_generation.users_data import generate_user_profiles
from src.pkm_app.tests.data_generation.projects_data import generate_projects
from src.pkm_app.tests.data_generation.sources_data import generate_sources
from src.pkm_app.tests.data_generation.keywords_data import generate_keywords
from src.pkm_app.tests.data_generation.notes_data import generate_notes
from src.pkm_app.tests.data_generation.note_links_data import generate_note_links
from src.pkm_app.tests.data_generation.sql_generator import generate_sql_inserts


def main():
    print("Generating test data for PKM application...")

    # Generate core entities
    users = generate_user_profiles()
    projects = generate_projects(users)
    sources = generate_sources(users)
    keywords = generate_keywords(users)

    # Generate notes with dependencies
    notes = generate_notes(users, projects, sources, keywords)

    # Generate note links
    note_links = generate_note_links(notes)

    print("Test data generation complete!")

    # Create data dictionary
    data = {
        "users": users,
        "projects": projects,
        "sources": sources,
        "keywords": keywords,
        "notes": notes,
        "note_links": note_links,
    }

    # Generate SQL inserts
    sql = generate_sql_inserts(data)

    # Create seed file
    seed_dir = "src/pkm_app/infrastructure/persistence/schema"
    os.makedirs(seed_dir, exist_ok=True)
    seed_path = os.path.join(seed_dir, "seed.sql")

    with open(seed_path, "w") as f:
        f.write("-- Seed data generated on " + datetime.now().isoformat() + "\n\n")
        f.write("\n".join(sql))
    print(f"Seed SQL file created at: {seed_path}")

    # Create Alembic migration file
    migrations_dir = "src/pkm_app/infrastructure/persistence/migrations/versions"
    os.makedirs(migrations_dir, exist_ok=True)
    migration_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    migration_filename = f"{migration_id}_seed_data.py"
    migration_path = os.path.join(migrations_dir, migration_filename)

    migration_content = f"""
\"\"\"Seed data migration

Revision ID: {migration_id}
Revises: e9e6a35c39f1
Create Date: {datetime.now().isoformat()}

\"\"\"
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '{migration_id}'
down_revision = 'e9e6a35c39f1'
branch_labels = None
depends_on = None


def upgrade():
    # Read seed data SQL
    with open('src/pkm_app/infrastructure/persistence/schema/seed.sql', 'r') as f:
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
"""

    with open(migration_path, "w") as f:
        f.write(migration_content)
    print(f"Alembic migration file created at: {migration_path}")

    return data


if __name__ == "__main__":
    main()
