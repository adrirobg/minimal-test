# Database Setup for Kairos BCP Development

## Overview

The Kairos BCP system uses PostgreSQL with the pgvector extension for vector similarity search. The database is automatically initialized when you start the development environment.

## Quick Start

1. **Start the development environment**:
   ```bash
   docker-compose up -d
   ```

2. **Wait for initialization** (about 30-60 seconds for first run)

3. **Access the database**:
   - **pgAdmin**: http://localhost:8080 (admin@kairos.dev / admin)
   - **Direct connection**: localhost:5432 (kairos_user / kairos_password)

## Database Configuration

- **Host**: localhost (or `postgres` from containers)
- **Port**: 5432
- **Database**: kairos_bcp_dev
- **Username**: kairos_user
- **Password**: kairos_password

## Initialization Process

The database is automatically initialized with:

1. **PostgreSQL with pgvector**: Vector similarity search capabilities
2. **Schema creation**: All tables created via Alembic migrations
3. **Sample data**: Test users, projects, and notes for immediate use

## Available Scripts

### Database Initialization
```bash
# Initialize database schema (run from backend directory)
python init_db.py
```

### Load Sample Data
```bash
# Create comprehensive sample data (run from backend directory)
python sample_data.py
```

### Reset Database
```bash
# Stop containers and remove database volume
docker-compose down -v
docker-compose up -d
```

## Sample Data

The system includes sample data for immediate testing:

### Test User
- **Email**: test@example.com
- **Username**: testuser
- **Password**: test123

### Development User (created by sample_data.py)
- **Email**: dev@kairos.local
- **Username**: developer
- **Password**: developer123

## Database Schema

The database follows Clean Architecture principles with these main entities:

- **users**: User authentication and profiles
- **projects**: Organizational containers for notes
- **notes**: Core content entities with vector embeddings
- **keywords**: Tagging system for categorization
- **sources**: External content references
- **note_links**: Bidirectional relationships between notes

## Vector Search

The system uses pgvector for semantic search:
- **Embedding column**: `notes.embeddings` (vector type)
- **Similarity search**: Uses cosine similarity for note matching
- **Indexing**: Optimized for fast similarity queries

## Development Workflow

1. **Make schema changes**: Edit SQLAlchemy models in `app/models/`
2. **Create migration**: `alembic revision --autogenerate -m "Description"`
3. **Apply migration**: `alembic upgrade head`
4. **Reset if needed**: `docker-compose down -v && docker-compose up -d`

## Troubleshooting

### Database won't start
```bash
# Check container logs
docker-compose logs postgres

# Restart with fresh database
docker-compose down -v
docker-compose up -d
```

### Connection issues
```bash
# Verify database is ready
docker-compose exec postgres pg_isready -U kairos_user -d kairos_bcp_dev

# Check port availability
netstat -an | grep 5432
```

### pgAdmin connection issues
1. Ensure PostgreSQL container is running
2. Use host `postgres` (not `localhost`) from pgAdmin container
3. Check pgAdmin logs: `docker-compose logs pgadmin`

### Migration issues
```bash
# View current migration status
alembic current

# View migration history
alembic history

# Reset to specific revision
alembic downgrade <revision>
```

## Performance Optimization

For development, the database is configured with:
- Moderate memory allocation (suitable for development)
- Optimized connection pooling
- Vector index optimization for semantic search
- Efficient query patterns for note relationships

## Backup and Restore

```bash
# Backup database
docker-compose exec postgres pg_dump -U kairos_user kairos_bcp_dev > backup.sql

# Restore database
docker-compose exec -T postgres psql -U kairos_user kairos_bcp_dev < backup.sql
```