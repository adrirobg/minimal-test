# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Kairos BCP** is a Personal Knowledge Management (PKM) system built with a pragmatic FastAPI backend and Next.js frontend architecture. The project consists of a Python FastAPI backend with PostgreSQL+pgvector database, and a Next.js 15 frontend with TypeScript, all orchestrated through Docker Compose for development.

## Architecture

The project follows **standard FastAPI application structure** with clear separation of concerns:

### Backend (`backend/app/`)
- **API Layer** (`backend/app/api/v1/`): FastAPI routers for all endpoints (auth, users, projects, notes, keywords, sources)
- **Core Layer** (`backend/app/core/`): Configuration, database connection, security utilities
- **Models Layer** (`backend/app/models/`): SQLAlchemy ORM models
- **Schemas Layer** (`backend/app/schemas/`): Pydantic request/response validation schemas
- **Main Application** (`backend/app/main.py`): FastAPI app creation and router configuration

### Frontend (`frontend/src/`)
- **App Router** (`frontend/src/app/`): Next.js 15 App Router pages and layouts
- **Components** (`frontend/src/components/`): Reusable React components with Shadcn/ui
- **Hooks** (`frontend/src/hooks/`): Custom React hooks
- **API Client** (`frontend/src/lib/`): API client utilities and type definitions
- **Types** (`frontend/src/types/`): TypeScript type definitions

Key architectural principles:
- FastAPI with async/await throughout (SQLAlchemy async)
- Standard FastAPI patterns and dependency injection
- PostgreSQL with pgvector for semantic search capabilities
- Docker Compose for development environment consistency

## Environment Setup & Configuration

### Initial Project Setup
```bash
# 1. Clone and setup environment files
cp .env.example .env

# 2. Configure database credentials in .env
DB_NAME="kairos_db"
DB_USER="kairos_user" 
DB_PASSWORD="strong_password_change_me"
PGADMIN_EMAIL="admin@kairos.dev"
PGADMIN_PASSWORD="admin"

# 3. Start development environment
docker-compose up -d

# 4. Wait for services to be healthy (30-60 seconds)
docker-compose ps  # Verify all services are "Up"
```

### Environment Variable Hierarchy
- **Development**: `.env` (local overrides)
- **Production**: Environment-specific injection
- **Required Variables**: DATABASE_URL, SECRET_KEY, CORS_ORIGINS
- **Optional Variables**: LOG_LEVEL, REDIS_URL, JWT_EXPIRE_MINUTES

### Quick Start
```bash
# Start entire development environment
docker-compose up -d

# Access applications
Frontend: http://localhost:3000
Backend API: http://localhost:8000/docs
Database: http://localhost:8080 (pgAdmin)
```

### Development Commands

#### Environment Management
```bash
# Start all services (recommended)
docker-compose up -d

# Stop all services
docker-compose down

# View service logs
docker-compose logs -f backend frontend

# Restart specific service
docker-compose restart backend
```

#### Backend Development (FastAPI)
```bash
# Enter backend container
docker-compose exec backend bash

# Install dependencies (inside container)
poetry install

# Database migrations
docker-compose exec backend alembic upgrade head                    # Apply migrations
docker-compose exec backend alembic revision --autogenerate -m ""  # Create new migration

# Direct database access
docker-compose exec postgres psql -U kairos -d kairos

# Run tests
docker-compose exec backend pytest                                  # Run all tests
docker-compose exec backend pytest tests/                          # Specific directory

# Code quality (inside container)
black app/                             # Format code
ruff check app/ --fix                  # Lint and fix
mypy app/                             # Type checking
```

#### Frontend Development (Next.js)
```bash
# Enter frontend container
docker-compose exec frontend bash

# Install dependencies (inside container)
npm install

# Development commands (inside container)
npm run dev        # Development server (already running)
npm run build      # Production build  
npm run start      # Production server
npm run lint       # ESLint
```

#### Database Management
```bash
# Access pgAdmin web interface
# http://localhost:8080
# Email: admin@kairos.dev
# Password: admin

# Command line database access
docker-compose exec postgres psql -U kairos -d kairos

# Load sample data
docker-compose exec backend python sample_data.py
```

## Key Domain Entities

- **User**: Authentication and user management with JWT tokens
- **Project**: Hierarchical organizational containers for notes
- **Note**: Core content entities with rich metadata and search capabilities
- **Keyword**: Tagging system for notes with bulk operations
- **Source**: External content references with flexible metadata
- **NoteLink**: Bidirectional relationships between notes (future feature)

## Database & Infrastructure

- **PostgreSQL 17** with **pgvector** extension for semantic search
- **SQLAlchemy 2.0** async ORM with optimized relationship loading
- **Alembic** for database schema migrations
- **Pydantic v2** for comprehensive data validation
- **Docker Compose** for consistent development environment
- **pgAdmin 4** for database management through web interface

## API Structure & Database Patterns

All API endpoints follow RESTful conventions under `/api/v1/`:

### Modern Async Database Dependency (SQLAlchemy 2.0)
```python
# Correct pattern matching actual codebase
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload
from app.core.database import get_async_session
from app.models.note import Note
from app.schemas.note import NoteCreate, NoteResponse

router = APIRouter()

@router.post("/notes/", response_model=NoteResponse)
async def create_note(
    note_data: NoteCreate,
    db: AsyncSession = Depends(get_async_session)  # Correct function name
):
    # Modern SQLAlchemy 2.0 async patterns
    async with db.begin():  # Explicit transaction management
        note = Note(**note_data.dict())
        db.add(note)
        await db.flush()  # Get ID without committing
        await db.refresh(note)
        return note

@router.get("/notes/", response_model=List[NoteResponse])
async def get_notes(
    db: AsyncSession = Depends(get_async_session)
):
    # Optimized relationship loading (2024 best practices)
    stmt = (
        select(Note)
        .options(
            selectinload(Note.keywords),  # Collections: selectinload
            joinedload(Note.project)      # Many-to-one: joinedload
        )
        .order_by(Note.created_at.desc())
    )
    result = await db.execute(stmt)
    return result.scalars().unique().all()
```

### Repository Pattern with Async Context Managers
```python
from contextlib import asynccontextmanager
from typing import AsyncContextManager

class NoteRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    @asynccontextmanager
    async def transaction(self) -> AsyncContextManager[AsyncSession]:
        """Explicit transaction boundary management."""
        try:
            yield self.session
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise
    
    async def create_with_relationships(self, note_data: dict) -> Note:
        """Create note with optimized relationship loading."""
        async with self.transaction():
            note = Note(**note_data)
            self.session.add(note)
            await self.session.flush()
            
            # Refresh with relationships loaded
            stmt = (
                select(Note)
                .options(selectinload(Note.keywords))
                .where(Note.id == note.id)
            )
            result = await self.session.execute(stmt)
            return result.scalar_one()
```

### Pydantic v2 Validation Patterns
```python
from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List
import re

class NoteCreate(BaseModel):
    """Pydantic v2 model with custom validation."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid"
    )
    
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    tags: Optional[List[str]] = Field(default_factory=list, max_length=10)
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()
    
    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v: List[str]) -> List[str]:
        validated_tags = []
        for tag in v:
            tag = tag.strip().lower()
            if not re.match(r'^[a-zA-Z0-9_-]+$', tag):
                raise ValueError(f'Tag "{tag}" contains invalid characters')
            validated_tags.append(tag)
        return validated_tags

class NoteResponse(BaseModel):
    """Response model with computed fields."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    title: str
    content: str
    tags: List[str]
    created_at: datetime
    
    @property
    def word_count(self) -> int:
        return len(self.content.split())
```

## Configuration

- **Environment Variables**: Managed via Pydantic Settings in `backend/app/core/config.py`
- **Docker Configuration**: `docker-compose.yml` for development services
- **Database Configuration**: Connection strings and pool settings
- **CORS Configuration**: Frontend/backend communication settings
- **JWT Configuration**: Token expiration and security settings

## Testing Structure

- **Backend Tests**: `backend/tests/` - Comprehensive FastAPI test suite
- **API Testing**: Interactive testing via Swagger UI at `/docs`
- **Database Testing**: Test database isolation and cleanup
- **Frontend Testing**: Playwright end-to-end testing capabilities

## Development Workflow

### Daily Development Process
See `DAILY_WORKFLOW.md` for detailed daily development instructions.

1. **Start Environment**: `docker-compose up -d` (2 minutes)
2. **Verify Services**: Check that all containers are running
3. **Development**: Edit files with automatic hot-reload
4. **Testing**: Use interactive API docs and frontend
5. **Database Work**: Use pgAdmin web interface

### API Development Pattern
1. **Define Schema**: Create Pydantic models in `backend/app/schemas/`
2. **Create Model**: Add SQLAlchemy model in `backend/app/models/`
3. **Build Router**: Implement endpoints in `backend/app/api/v1/`
4. **Test Endpoint**: Use Swagger UI at `/docs`
5. **Frontend Integration**: Connect from Next.js components

### Database Changes
1. **Modify Models**: Update SQLAlchemy models
2. **Generate Migration**: `docker-compose exec backend alembic revision --autogenerate -m "description"`
3. **Apply Migration**: `docker-compose exec backend alembic upgrade head`
4. **Verify Changes**: Check in pgAdmin or database directly

## Key Files

- `CURRENT_STATE.md`: **Current project status and architecture overview**
- `API_DOCUMENTATION.md`: **Comprehensive API reference with examples**
- `DAILY_WORKFLOW.md`: **Daily development workflow and productivity tips**
- `docker-compose.yml`: **Development environment configuration**
- `backend/app/main.py`: **FastAPI application entry point**
- `backend/app/core/config.py`: **Application configuration and settings**
- `backend/pyproject.toml`: **Python dependencies and tool configuration**
- `frontend/package.json`: **Frontend dependencies and scripts**
- `backend/migrations/versions/`: **Database migration files**
- `backend/tests/`: **Backend test suite**

## Branch Strategy

- `main`: Production-ready stable code
- `experiment-rewrite-v1`: Current active development branch (successful architecture rewrite)

## Code Quality Standards

### Backend (Python)
- **Type Hints**: Use throughout with mypy validation
- **Async Patterns**: Async/await for all database operations
- **Pydantic Validation**: Comprehensive request/response validation
- **Error Handling**: Structured error responses with proper HTTP codes
- **Documentation**: Docstrings and OpenAPI documentation

### Frontend (TypeScript)
- **TypeScript**: Strict mode with comprehensive type safety
- **React Patterns**: Modern hooks and functional components
- **Component Structure**: Shadcn/ui components with consistent styling
- **State Management**: Zustand for application state
- **Forms**: React Hook Form with Zod validation

## Important Development Notes

### Hot-Reload Development
- **Backend**: FastAPI auto-reloads on file changes in `backend/app/`
- **Frontend**: Next.js hot-reloads on changes in `frontend/src/`
- **Database**: Changes require migration and container restart

### API Testing
- **Interactive Docs**: Always available at `http://localhost:8000/docs`
- **Authentication**: Use JWT tokens from login endpoint
- **Data Validation**: Comprehensive Pydantic validation on all endpoints

### Docker Environment
- **Consistency**: All developers use identical environment
- **Data Persistence**: Database data persists between container restarts
- **Port Conflicts**: Ensure ports 3000, 8000, 5432, 8080 are available

### Current Project Status
The project represents a **successful architectural rewrite** from a complex Clean Architecture approach to a pragmatic, maintainable FastAPI structure. All core PKM functionality is implemented and working, with comprehensive documentation and a professional development environment.

## Code Generation Templates

### Creating New API Endpoint
```python
# 1. Define Pydantic schemas (backend/app/schemas/entity_name.py)
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

class EntityCreate(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid"
    )
    
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None

class EntityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    description: Optional[str]
    created_at: datetime

# 2. Create SQLAlchemy model (backend/app/models/entity_name.py)
from sqlalchemy import String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base
from datetime import datetime

class Entity(Base):
    __tablename__ = "entities"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

# 3. Create API router (backend/app/api/v1/entities.py)
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_async_session
from app.models.entity_name import Entity
from app.schemas.entity_name import EntityCreate, EntityResponse

router = APIRouter()

@router.post("/", response_model=EntityResponse)
async def create_entity(
    entity_data: EntityCreate,
    db: AsyncSession = Depends(get_async_session)
):
    async with db.begin():
        entity = Entity(**entity_data.dict())
        db.add(entity)
        await db.flush()
        await db.refresh(entity)
        return entity

@router.get("/{entity_id}", response_model=EntityResponse)
async def get_entity(
    entity_id: int,
    db: AsyncSession = Depends(get_async_session)
):
    stmt = select(Entity).where(Entity.id == entity_id)
    result = await db.execute(stmt)
    entity = result.scalar_one_or_none()
    
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    
    return entity

# 4. Register router in main.py
# Add to backend/app/main.py:
# from app.api.v1 import entities
# app.include_router(entities.router, prefix="/api/v1/entities", tags=["entities"])
```

### Creating React Component (Frontend)
```typescript
// frontend/src/components/EntityForm.tsx
'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { useToast } from '@/hooks/use-toast';

const entitySchema = z.object({
  name: z.string().min(1, 'Name is required').max(200),
  description: z.string().optional(),
});

type EntityFormData = z.infer<typeof entitySchema>;

interface EntityFormProps {
  onSuccess?: () => void;
}

export function EntityForm({ onSuccess }: EntityFormProps) {
  const { toast } = useToast();
  const form = useForm<EntityFormData>({
    resolver: zodResolver(entitySchema),
    defaultValues: {
      name: '',
      description: '',
    },
  });

  async function onSubmit(data: EntityFormData) {
    try {
      const response = await fetch('/api/v1/entities/', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${getAuthToken()}`, // Implement auth token getter
        },
        body: JSON.stringify(data),
      });
      
      if (!response.ok) {
        throw new Error('Failed to create entity');
      }
      
      const entity = await response.json();
      
      toast({
        title: "Success",
        description: "Entity created successfully.",
      });
      
      form.reset();
      onSuccess?.();
      
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to create entity. Please try again.",
        variant: "destructive",
      });
    }
  }

  return (
    <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <Input 
          {...form.register('name')} 
          placeholder="Entity name"
          error={form.formState.errors.name?.message}
        />
      </div>
      
      <div>
        <Textarea 
          {...form.register('description')} 
          placeholder="Description (optional)"
          error={form.formState.errors.description?.message}
        />
      </div>
      
      <Button 
        type="submit" 
        disabled={form.formState.isSubmitting}
      >
        {form.formState.isSubmitting ? 'Creating...' : 'Create Entity'}
      </Button>
    </form>
  );
}

// Usage in a page:
// frontend/src/app/entities/page.tsx
export default function EntitiesPage() {
  return (
    <div className="container mx-auto py-8">
      <h1 className="text-2xl font-bold mb-6">Entities</h1>
      <EntityForm onSuccess={() => window.location.reload()} />
    </div>
  );
}
```

### Database Migration Template
```bash
# Generate migration after model changes
docker-compose exec backend alembic revision --autogenerate -m "add_entity_table"

# Review generated migration file in backend/migrations/versions/
# Edit if necessary, then apply:
docker-compose exec backend alembic upgrade head

# Rollback if needed:
docker-compose exec backend alembic downgrade -1
```

## Troubleshooting & Common Issues

### Docker Development Issues

#### Service Won't Start
```bash
# Check service status
docker-compose ps

# View detailed logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres

# Restart specific service
docker-compose restart backend

# Rebuild if dependencies changed
docker-compose build backend --no-cache
```

#### Port Conflicts
```bash
# Check port usage
lsof -i :3000
lsof -i :8000
lsof -i :5432

# Use alternative ports in docker-compose.yml
ports:
  - "3001:3000"  # external:internal
  - "8001:8000"
  - "5433:5432"
```

#### Database Connection Issues
```bash
# Test database connectivity
docker-compose exec postgres pg_isready -U kairos

# Check database logs
docker-compose logs postgres

# Reset database if corrupted
docker-compose down -v
docker-compose up -d

# Manual database access
docker-compose exec postgres psql -U kairos -d kairos
```

#### Volume and Permission Issues
```bash
# Fix volume permissions (Linux/WSL)
sudo chown -R $USER:$USER ./backend
sudo chown -R $USER:$USER ./frontend

# Clear Docker cache if needed
docker system prune -a

# Reset all volumes (WARNING: deletes all data)
docker-compose down -v
docker volume prune
```

### FastAPI Development Issues

#### Authentication Token Problems
- Verify JWT_SECRET_KEY is set correctly in `.env`
- Check token expiration (default: 30 minutes)
- Use `/docs` interactive auth for testing:
  1. Go to http://localhost:8000/docs
  2. Click "Authorize" button
  3. Use login endpoint to get token
  4. Enter token in authorization dialog

#### API Validation Errors (Pydantic v2)
```python
# Debug validation issues
from pydantic import ValidationError

try:
    data = NoteCreate(**request_data)
except ValidationError as e:
    print("Validation errors:")
    for error in e.errors():
        print(f"Field: {error['loc']}, Error: {error['msg']}")
```

#### Database Session Issues
```python
# Always use async context managers
async with get_async_session() as session:
    # Database operations here
    pass

# For transactions, use explicit begin()
async with session.begin():
    # Transactional operations
    pass
```

### Frontend Development Issues

#### Next.js Build Errors
```bash
# Clear Next.js cache
rm -rf frontend/.next
rm -rf frontend/node_modules
cd frontend && npm install

# Check TypeScript errors
cd frontend && npm run build
```

#### API Connection Issues
- Verify `NEXT_PUBLIC_API_URL` in `frontend/.env.local`
- Check CORS settings in FastAPI backend
- Test API endpoints directly: http://localhost:8000/docs

#### Authentication Flow Issues
- Check token storage and retrieval
- Verify token format (Bearer token)
- Test authentication endpoints manually

### Performance Issues

#### Slow Database Queries
```python
# Use selectinload for collections (optimal in 2024)
from sqlalchemy.orm import selectinload, joinedload

stmt = select(Note).options(
    selectinload(Note.keywords),  # For collections
    joinedload(Note.project)      # For single relationships
)
```

#### Memory Usage
```bash
# Monitor Docker resource usage
docker stats

# Increase Docker memory limits if needed
# Docker Desktop -> Settings -> Resources
```

### Getting Help

1. **Check logs first**: `docker-compose logs [service]`
2. **Read error messages carefully** - they usually contain the solution
3. **Consult documentation**: `API_DOCUMENTATION.md`, `DAILY_WORKFLOW.md`
4. **Use interactive API docs**: http://localhost:8000/docs
5. **Test components separately**: API, database, frontend
6. **Reset environment if stuck**: `docker-compose down -v && docker-compose up -d`

## Security Best Practices

### JWT Authentication Implementation
```python
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

SECRET_KEY = "your-secret-key-here"  # Use environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/token")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = await get_user_by_username(username)
    if user is None:
        raise credentials_exception
    return user
```

### Input Validation and Sanitization
```python
from pydantic import BaseModel, Field, field_validator
import html

class SecureNoteCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1, max_length=10000)
    
    @field_validator('title', 'content')
    @classmethod
    def sanitize_html(cls, v: str) -> str:
        return html.escape(v.strip())
```

## Performance Optimization

### Database Query Optimization
```python
from sqlalchemy.orm import selectinload

# Optimized relationship loading
stmt = (
    select(Note)
    .options(
        selectinload(Note.keywords),  # Collections: selectinload
        joinedload(Note.project)      # Many-to-one: joinedload
    )
    .order_by(Note.created_at.desc())
)

# Cursor-based pagination for large datasets
async def get_notes_paginated(db: AsyncSession, limit: int = 20, cursor: str = None):
    stmt = select(Note).limit(limit + 1)
    if cursor:
        stmt = stmt.where(Note.id < cursor)
    
    result = await db.execute(stmt)
    notes = result.scalars().all()
    
    has_more = len(notes) > limit
    if has_more:
        notes = notes[:-1]
    
    return {"notes": notes, "has_more": has_more}
```

### Caching Strategies
```python
import redis.asyncio as redis
from functools import wraps

redis_client = redis.from_url("redis://localhost:6379")

def cache_result(expiry: int = 300):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            cached = await redis_client.get(cache_key)
            if cached:
                return pickle.loads(cached)
            
            result = await func(*args, **kwargs)
            await redis_client.setex(cache_key, expiry, pickle.dumps(result))
            return result
        return wrapper
    return decorator
```

## Testing Patterns

### Test Configuration
```python
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest_asyncio.fixture
async def test_client():
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncClient(transport=ASGITransport(app=app)) as client:
        yield client
    
    await engine.dispose()

@pytest.mark.asyncio
async def test_create_note(test_client: AsyncClient):
    response = await test_client.post("/api/v1/notes/", json={
        "title": "Test Note",
        "content": "Test content"
    })
    assert response.status_code == 201
    assert "id" in response.json()
```

## Development Standards

### Code Organization
- Separation of concerns: services, repositories, controllers
- Dependency injection for database sessions
- Type safety: TypeScript frontend, Python type hints
- Comprehensive error handling

### Security Requirements
- Input validation and sanitization
- JWT authentication with proper expiration
- Password hashing with bcrypt
- CORS configuration
- SQL injection prevention via ORM

### Performance Guidelines
- Use selectinload for collections, joinedload for single relationships
- Cursor-based pagination for large datasets
- Redis caching for frequently accessed data
- Background tasks for non-critical operations
- Database query monitoring

### Testing Strategy
- Unit tests for business logic
- Integration tests for API endpoints
- Database isolation and cleanup
- Mock external dependencies

## Parallel Task Execution Guidelines

### When to Use Parallel Tasks

**Always Use Parallel Tasks For:**
- **Technology Stack Research**: Investigating multiple libraries/frameworks simultaneously
- **Multi-Component Analysis**: Analyzing different parts of the codebase independently
- **Cross-Domain Information Gathering**: Backend + Frontend + Database + DevOps research
- **Independent Problem Solving**: Multiple issues that don't depend on each other
- **Comparative Analysis**: Evaluating different approaches or solutions

**Sequential Tasks When:**
- Tasks depend on results from previous tasks
- Single, focused research topic
- Simple operations that execute quickly
- Information building requires context from previous steps

### Parallel Task Structure Patterns

#### Pattern 1: Technology Stack Investigation
```
Task 1: Backend technology research (FastAPI, SQLAlchemy)
Task 2: Frontend technology research (Next.js, React patterns)  
Task 3: Database optimization research (PostgreSQL, performance)
Task 4: DevOps patterns research (Docker, deployment)
WebSearch: Specific integration patterns
```

#### Pattern 2: Multi-Component Problem Analysis
```
Task 1: Analyze authentication flow issues
Task 2: Investigate database performance problems
Task 3: Review frontend state management  
Task 4: Examine API endpoint design
```

#### Pattern 3: Comprehensive Feature Implementation
```
Task 1: Research backend implementation patterns
Task 2: Research frontend component patterns
Task 3: Research testing strategies
Task 4: Research security considerations
```

### Task Design Principles

**1. Independence First**
- Each task must be able to execute without results from other tasks
- Clearly separate concerns and domains
- Avoid overlapping research areas

**2. Specific and Focused Prompts**
- Detailed task descriptions with clear objectives
- Specify exact technologies, versions, and patterns needed
- Include expected output format and depth

**3. Balanced Scope**
- Not too narrow (inefficient parallelization)
- Not too broad (loses focus and depth)
- Aim for 15-30 minutes of equivalent sequential work per task

**4. Clear Integration Strategy**
- Plan how results will be combined
- Ensure outputs are in compatible formats
- Consider interdependencies in final integration

### Execution Decision Matrix

| Scenario | Use Parallel Tasks | Reasoning |
|----------|-------------------|-----------|
| Research 3+ technologies | Yes | Independent domains, significant time savings |
| Analyze codebase sections | Yes | Different components, independent analysis |
| Debug multiple unrelated issues | Yes | Separate problem spaces |
| Implement complex feature | Yes | Backend/Frontend/Testing can be researched in parallel |
| Follow step-by-step tutorial | No | Sequential dependency |
| Simple bug fix | No | Single focus area |
| Quick information lookup | No | Overhead not justified |

### Example Implementation

**Instead of Sequential:**
```
1. Research FastAPI patterns (5 min)
2. Research SQLAlchemy patterns (5 min)  
3. Research Next.js patterns (5 min)
4. Research Docker patterns (5 min)
Total: 20 minutes
```

**Use Parallel Approach:**
```python
# Single message with multiple concurrent tasks
Task 1: FastAPI async patterns and best practices
Task 2: SQLAlchemy 2.0 relationship loading optimization  
Task 3: Next.js 15 App Router with TypeScript patterns
Task 4: Docker Compose development environment optimization
Total: 6-8 minutes with deeper coverage
```

### Integration Best Practices

**1. Synthesize Results**
- Identify common patterns across task outputs
- Resolve any conflicting recommendations
- Create unified implementation approach

**2. Cross-Reference Findings**
- Look for integration points between different research areas
- Identify potential conflicts or compatibility issues
- Ensure consistency across technology stack

**3. Prioritize Implementation**
- Use research depth to inform implementation order
- Consider dependencies revealed through parallel research
- Plan staged rollout based on complexity and risk

### Quality Assurance

**Before Parallel Execution:**
- Verify tasks are truly independent
- Ensure each task has clear, specific objectives
- Confirm combined scope justifies parallel approach

**During Execution:**
- Monitor for overlapping or duplicate research
- Adjust scope if tasks complete too quickly or slowly

**After Completion:**
- Validate all areas were adequately covered
- Check for gaps between task boundaries
- Ensure integration produces coherent outcome

### Performance Metrics

**Efficiency Indicators:**
- Time savings: Target 60-70% reduction in research time
- Coverage depth: Each parallel task should match sequential depth
- Integration quality: Results should synthesize into coherent guidelines
- Implementation readiness: Outputs should be immediately actionable

**When Parallel Tasks Succeed:**
- All areas adequately researched without gaps
- Clear integration path between different research areas  
- Significant time savings without quality compromise
- Actionable recommendations across full scope

This methodology should be applied whenever Claude Code encounters complex, multi-faceted tasks that can benefit from parallel investigation and analysis.