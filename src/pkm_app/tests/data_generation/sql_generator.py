"""
Module for converting generated test data to SQL insert statements
"""

import json


def generate_sql_inserts(data):
    """
    Convert generated test data to SQL insert statements
    Returns list of SQL statements
    """
    sql_statements = []

    # Generate SQL for users - using real schema
    for user in data["users"]:
        sql = f"""
        INSERT INTO user_profiles (user_id, name, email, preferences, created_at, updated_at)
        VALUES (
            '{user.id}',
            {f"'{user.display_name.replace("'", "''")}'" if user.display_name else 'NULL'},
            '{user.email}',
            '{json.dumps(user.preferences)}',
            '{user.created_at.isoformat()}',
            '{user.updated_at.isoformat()}'
        );
        """
        sql_statements.append(sql)

    # Generate SQL for projects - using real schema
    for project in data["projects"]:
        owner_id = project.metadata.get("owner_id")
        sql = f"""
        INSERT INTO projects (id, user_id, name, description, created_at, updated_at)
        VALUES (
            '{project.id}',
            '{owner_id}',
            '{project.name.replace("'", "''")}',
            '{project.description.replace("'", "''")}',
            '{project.created_at.isoformat()}',
            '{project.updated_at.isoformat()}'
        );
        """
        sql_statements.append(sql)

    # Generate SQL for sources - using real schema
    for source in data["sources"]:
        user_id = source.metadata.get("user_id")
        description = source.metadata.get("description", "")
        sql = f"""
        INSERT INTO sources (id, user_id, type, title, description, url, created_at, updated_at)
        VALUES (
            '{source.id}',
            '{user_id}',
            '{source.source_type}',
            '{source.title.replace("'", "''")}',
            '{description.replace("'", "''")}',
            {f"'{source.url}'" if source.url else 'NULL'},
            '{source.created_at.isoformat()}',
            '{source.updated_at.isoformat()}'
        );
        """
        sql_statements.append(sql)

    # Generate SQL for keywords - using real schema
    for keyword in data["keywords"]:
        sql = f"""
        INSERT INTO keywords (id, user_id, name, created_at)
        VALUES (
            '{keyword.id}',
            '{keyword.user_id}',
            '{keyword.name.replace("'", "''")}',
            '{keyword.created_at.isoformat()}'
        );
        """
        sql_statements.append(sql)

    # Generate SQL for notes - using real schema
    for note in data["notes"]:
        user_id = note.metadata.get("user_id")
        sql = f"""
        INSERT INTO notes (id, user_id, project_id, source_id, title, content, type, note_metadata, created_at, updated_at)
        VALUES (
            '{note.id}',
            '{user_id}',
            '{note.project_id}',
            {f"'{note.source_id}'" if note.source_id else 'NULL'},
            '{note.title.replace("'", "''")}',
            '{note.content.replace("'", "''")}',
            '{note.type}',
            '{json.dumps(note.metadata)}',
            '{note.created_at.isoformat()}',
            '{note.updated_at.isoformat()}'
        );
        """
        sql_statements.append(sql)

        # Generate SQL for note-keyword associations
        for keyword_id in note.keyword_ids:
            sql = f"""
            INSERT INTO note_keywords (note_id, keyword_id)
            VALUES ('{note.id}', '{keyword_id}');
            """
            sql_statements.append(sql)

    # Generate SQL for note links - using real schema
    for link in data["note_links"]:
        # Get user_id from source note
        source_note = next((n for n in data["notes"] if n.id == link.source_note_id), None)
        user_id = source_note.metadata.get("user_id") if source_note else None

        sql = f"""
        INSERT INTO note_links (id, source_note_id, target_note_id, link_type, user_id, created_at)
        VALUES (
            '{link.id}',
            '{link.source_note_id}',
            '{link.target_note_id}',
            '{link.link_type}',
            '{user_id}',
            '{link.created_at.isoformat()}'
        );
        """
        sql_statements.append(sql)

    return sql_statements
