# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Kairos BCP** is a Personal Knowledge Management (PKM) system built with Clean Architecture principles. The project consists of a Python backend using FastAPI/SQLAlchemy with PostgreSQL+pgvector, and a Next.js frontend with TypeScript.

## Architecture

The backend follows **Clean Architecture** with strict separation of concerns:

- **Domain Layer** (`src/pkm_app/core/domain/`): Core entities (Note, Project, Source, Keyword, etc.) using Pydantic
- **Application Layer** (`src/pkm_app/core/application/`): Use cases, DTOs, and repository interfaces  
- **Infrastructure Layer** (`src/pkm_app/infrastructure/`): SQLAlchemy repositories, database models, Streamlit UI, FastAPI endpoints

Key architectural principles:
- All dependencies point inward toward the domain
- Async/await throughout (SQLAlchemy async, asyncio.run() for Streamlit)
- Repository pattern for data access
- Unit of Work pattern for transaction management

## Development Commands

### Backend (Python)
```bash
# Install dependencies (Poetry required)
poetry install

# Database migrations
alembic upgrade head                    # Apply migrations
alembic revision --autogenerate -m ""  # Create new migration

# Run Streamlit UI
streamlit run src/pkm_app/infrastructure/web/streamlit_ui/app.py

# Testing
pytest                                  # Run all tests
pytest src/pkm_app/tests/unit/         # Unit tests only
pytest src/pkm_app/tests/integration/  # Integration tests only

# Code quality
black src/                             # Format code
ruff check src/ --fix                  # Lint and fix
mypy src/pkm_app                      # Type checking
pre-commit run --all-files            # Run all pre-commit hooks
```

### Frontend (Next.js)
```bash
cd frontend/
npm run dev        # Development server with Turbopack
npm run build      # Production build  
npm run start      # Production server
npm run lint       # ESLint
```

### Docker
```bash
docker-compose up -d    # Start PostgreSQL + pgAdmin + Qdrant
docker-compose down     # Stop services
```

## Key Domain Entities

- **Note**: Core content entity with title, content, type, metadata
- **Project**: Organizational container for notes
- **Source**: External content sources 
- **Keyword**: Tagging system for notes
- **NoteLink**: Bidirectional links between notes
- **UserProfile**: User management

## Database & Infrastructure

- **PostgreSQL 17** with **pgvector** extension for semantic search
- **SQLAlchemy 2.0** async ORM with relationship loading optimization
- **Alembic** for database migrations
- **Pydantic** for data validation across all layers
- **Qdrant** vector database for advanced search capabilities

## Repository Patterns

All repositories follow async patterns:
```python
# Repository interface in application layer
class INoteRepository(ABC):
    async def get_by_id(self, note_id: uuid.UUID, user_id: str) -> NoteSchema | None:
    
# Implementation in infrastructure layer  
class SQLAlchemyNoteRepository(INoteRepository):
    def __init__(self, session: AsyncSession):
```

## Testing Structure

- **Unit tests**: `src/pkm_app/tests/unit/` - Test domain logic and use cases with mocks
- **Integration tests**: `src/pkm_app/tests/integration/` - Test repository implementations with real database
- **Test data generation**: `src/pkm_app/tests/data_generation/` - Faker-based test data creation

## Configuration

- Environment variables managed via Pydantic Settings
- Docker Compose for local development environment
- Pre-commit hooks for code quality (Black, Ruff, MyPy)
- Frontend uses Next.js 15 with App Router, TypeScript, Tailwind CSS, Shadcn/ui

## Key Files

- `pyproject.toml`: Python dependencies and tool configuration
- `alembic.ini`: Database migration configuration  
- `docker-compose.yml`: Local development services
- `frontend/package.json`: Frontend dependencies and scripts
- Database migrations: `src/pkm_app/infrastructure/persistence/migrations/versions/`