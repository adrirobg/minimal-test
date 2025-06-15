# Kairos BCP Backend

Personal Knowledge Management System backend API built with FastAPI, SQLAlchemy, and PostgreSQL.

## Features

- FastAPI REST API
- PostgreSQL database with async SQLAlchemy
- User authentication and authorization
- Notes, Projects, Sources, and Keywords management
- Database migrations with Alembic

## Development

```bash
# Install dependencies
poetry install

# Run development server
poetry run uvicorn app.main:app --reload

# Database migrations
poetry run alembic upgrade head
```