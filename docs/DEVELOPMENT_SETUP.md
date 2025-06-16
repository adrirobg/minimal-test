# WSL Development Setup Guide for Kairos BCP

**WSL-optimized development workflow - get coding in under 10 minutes!**

This guide is optimized for WSL (Windows Subsystem for Linux) development, providing the fastest and most consistent development experience for Kairos BCP.

## 🚀 Quick Start (10 minutes)

### Prerequisites
- **WSL 2** with Ubuntu 22.04 LTS (see [WSL Quick Start Guide](WSL_QUICK_START.md))
- **Docker** running in WSL
- **Git** for version control

### 1. Clone and Start (5 minutes)
```bash
# Ensure you're in WSL native file system for best performance
cd ~/projects

# Clone the repository
git clone [repository-url] kairos-bcp
cd kairos-bcp

# Start everything with one command
docker-compose up -d

# Wait 30-60 seconds for services to start
```

### 2. Access Your Development Environment (2 minutes)
- **Frontend**: http://localhost:3000 (Next.js with hot-reload)
- **Backend API**: http://localhost:8000 (FastAPI with auto-reload)
- **API Docs**: http://localhost:8000/docs (Interactive Swagger UI)
- **Database Admin**: http://localhost:8080 (pgAdmin - admin@kairos.dev / admin)

### 3. Start Coding! (3 minutes)
```bash
# Open VS Code in WSL mode
code .

# Edit backend code in integrated terminal
cd backend && poetry shell

# Edit frontend code in another terminal
cd frontend && npm run dev

# View logs in real-time
docker-compose logs -f backend
docker-compose logs -f frontend
```

**That's it!** Your complete WSL development environment is running with hot-reloading enabled.

## 🔧 WSL Development Details

### System Requirements
- **WSL 2** on Windows 10 (version 2004+) or Windows 11
- **8GB+ RAM**: Recommended for optimal WSL performance  
- **20GB+ Storage**: For WSL distribution, Docker images and code

### Required Software (Install Once)
```bash
# WSL 2 with Ubuntu 22.04 LTS
wsl --install

# VS Code with Remote-WSL extension (Windows)
# Download from: https://code.visualstudio.com/
# Install Remote-WSL extension

# All other tools install inside WSL (see WSL_QUICK_START.md)
```

### WSL Performance Optimization
For optimal performance (see [WSL Performance Tips](WSL_PERFORMANCE_TIPS.md)):

#### File System Location
```bash
# ✅ FAST: Work in WSL native file system
~/projects/kairos-bcp/

# ❌ SLOW: Avoid Windows file system
/mnt/c/Users/Username/Projects/kairos-bcp/
```

#### Development Tools in WSL
```bash
# Install tools inside WSL for best performance
# Python with Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Node.js with nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install --lts

# Docker native in WSL
curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh
```

## 📋 Daily WSL Development Workflow

### Start Your Development Session
```bash
# Open WSL terminal or VS Code integrated terminal
cd ~/projects/kairos-bcp

# Start everything (one command does it all!)
docker-compose up -d

# Open VS Code in WSL mode
code .

# View what's running
docker-compose ps

# Follow logs for debugging
docker-compose logs -f
```

### Stop Your Development Session
```bash
# Stop all services
docker-compose down

# Stop and remove data (fresh start)
docker-compose down -v
```

### Make Code Changes
- **Backend changes**: Edit files in `backend/app/` - auto-reloads
- **Frontend changes**: Edit files in `frontend/src/` - auto-reloads
- **Database**: Use pgAdmin at http://localhost:8080 for queries

### Test Your Changes
```bash
# Quick test endpoints
curl http://localhost:8000/health
curl http://localhost:8000/docs

# View frontend
open http://localhost:3000
```

## Backend Development

### 1. Setup Python Environment

```bash
cd backend/

# Install dependencies
poetry install

# Activate virtual environment
poetry shell

# Or use poetry run for individual commands
poetry run python --version
```

### 2. Database Migration

```bash
# Run database migrations
poetry run alembic upgrade head

# Create new migration (when needed)
poetry run alembic revision --autogenerate -m "Description of changes"

# Check migration status
poetry run alembic current
poetry run alembic history
```

### 3. Start Backend Development Server

```bash
# Option 1: Using Poetry
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Option 2: Using Python module
poetry run python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Option 3: Using Docker (development mode)
docker-compose up backend
```

### 4. Backend Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── core/
│   │   ├── config.py        # Configuration settings
│   │   ├── security.py      # Authentication & authorization
│   │   └── database.py      # Database connection
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── api/
│   │   ├── v1/             # API version 1 routes
│   │   └── dependencies.py  # Dependency injection
│   ├── services/           # Business logic
│   └── utils/              # Utility functions
├── migrations/             # Alembic migrations
├── tests/                  # Test files
├── pyproject.toml         # Poetry configuration
└── Dockerfile             # Docker configuration
```

### 5. Backend Development Commands

```bash
# Run tests
poetry run pytest

# Run tests with coverage
poetry run pytest --cov=app

# Run specific test file
poetry run pytest tests/test_main.py

# Code formatting
poetry run black app/ tests/

# Linting
poetry run ruff check app/ tests/

# Type checking
poetry run mypy app/

# Start interactive shell
poetry run python

# Database operations
poetry run alembic upgrade head          # Apply migrations
poetry run alembic downgrade -1         # Rollback one migration
poetry run alembic show current         # Show current migration
```

## Frontend Development

### 1. Setup Node.js Environment

```bash
cd frontend/

# Install dependencies
npm install

# Or use specific commands
npm ci  # For clean installations
```

### 2. Start Frontend Development Server

```bash
# Start development server
npm run dev

# Start with specific port
npm run dev -- --port 3001

# Start with Docker
docker-compose up frontend
```

### 3. Frontend Project Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── layout.tsx         # Root layout
│   │   ├── page.tsx           # Home page
│   │   ├── (auth)/            # Authentication pages
│   │   ├── dashboard/         # Dashboard pages
│   │   └── api/               # API routes
│   ├── components/
│   │   ├── ui/                # Reusable UI components
│   │   ├── forms/             # Form components
│   │   ├── layout/            # Layout components
│   │   └── features/          # Feature-specific components
│   ├── hooks/                 # Custom React hooks
│   ├── lib/                   # Utility libraries
│   ├── styles/                # CSS and styling
│   └── types/                 # TypeScript type definitions
├── public/                    # Static assets
├── package.json              # Dependencies and scripts
├── next.config.js            # Next.js configuration
├── tailwind.config.js        # Tailwind CSS configuration
├── tsconfig.json             # TypeScript configuration
└── Dockerfile                # Docker configuration
```

### 4. Frontend Development Commands

```bash
# Development server
npm run dev

# Production build
npm run build

# Start production server
npm run start

# Linting
npm run lint

# Type checking
npm run type-check

# Testing (if configured)
npm run test

# Storybook (if configured)
npm run storybook

# Bundle analysis
npm run analyze
```

## Database Setup

### 1. PostgreSQL with Docker

```bash
# Start PostgreSQL
docker-compose up -d postgres

# Connect to database
docker exec -it kairos-postgres-dev psql -U kairos_user -d kairos_bcp_dev

# View database logs
docker-compose logs postgres
```

### 2. Database Management

```bash
# Access pgAdmin
# Visit http://localhost:5050
# Login: admin@kairos.dev / admin

# Manual database operations
docker exec -it kairos-postgres-dev psql -U kairos_user -d kairos_bcp_dev -c "SELECT version();"

# Backup database
docker exec kairos-postgres-dev pg_dump -U kairos_user kairos_bcp_dev > backup.sql

# Restore database
docker exec -i kairos-postgres-dev psql -U kairos_user kairos_bcp_dev < backup.sql
```

### 3. Sample Data

```bash
# Load sample data (if available)
cd backend/
poetry run python scripts/load_sample_data.py

# Or via SQL
docker exec -i kairos-postgres-dev psql -U kairos_user kairos_bcp_dev < sample_data.sql
```

## Development Workflow

### 1. Daily Development Routine

1. **Start Development Environment**
   ```bash
   # Terminal 1: Infrastructure
   docker-compose up -d postgres redis
   
   # Terminal 2: Backend
   cd backend && poetry run uvicorn app.main:app --reload
   
   # Terminal 3: Frontend
   cd frontend && npm run dev
   ```

2. **Check Application Status**
   - Backend API: http://localhost:8000
   - Frontend App: http://localhost:3000
   - API Documentation: http://localhost:8000/docs
   - pgAdmin: http://localhost:5050

### 2. Git Workflow

```bash
# Feature development
git checkout develop
git pull origin develop
git checkout -b feature/your-feature-name

# Make changes and commit
git add .
git commit -m "feat: add new feature"

# Push and create pull request
git push origin feature/your-feature-name
```

### 3. Code Review Process

1. **Before Submitting PR**
   ```bash
   # Run backend checks
   cd backend/
   poetry run black app/ tests/
   poetry run ruff check app/ tests/
   poetry run mypy app/
   poetry run pytest
   
   # Run frontend checks
   cd frontend/
   npm run lint
   npm run type-check
   npm run build
   ```

2. **PR Checklist**
   - [ ] All tests pass
   - [ ] Code is properly formatted
   - [ ] Type checking passes
   - [ ] Documentation updated
   - [ ] No security vulnerabilities
   - [ ] Performance impact considered

## Testing Environment

### 1. Backend Testing

```bash
cd backend/

# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=app --cov-report=html

# Run specific test categories
poetry run pytest tests/unit/
poetry run pytest tests/integration/
poetry run pytest tests/e2e/

# Run tests with verbose output
poetry run pytest -v

# Run tests matching pattern
poetry run pytest -k "test_user"
```

### 2. Frontend Testing

```bash
cd frontend/

# Run unit tests (if configured)
npm run test

# Run e2e tests (if configured)
npm run test:e2e

# Run visual regression tests (if configured)
npm run test:visual
```

### 3. Integration Testing

```bash
# Run full integration tests
cd tests/
poetry run pytest e2e/

# Run with browser UI (if using Playwright)
poetry run pytest e2e/ --headed

# Run specific browser
poetry run pytest e2e/ --browser=chromium
```

### 4. Test Data Management

```bash
# Create test database
docker exec kairos-postgres-dev createdb -U kairos_user kairos_bcp_test

# Load test data
cd backend/
poetry run python scripts/load_test_data.py

# Reset test database
poetry run python scripts/reset_test_db.py
```

## Code Quality Tools

### 1. Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

### 2. Backend Code Quality

```bash
cd backend/

# Formatting
poetry run black app/ tests/

# Import sorting
poetry run isort app/ tests/

# Linting
poetry run ruff check app/ tests/

# Type checking
poetry run mypy app/

# Security scanning
poetry run bandit -r app/

# Dependency checking
poetry run safety check
```

### 3. Frontend Code Quality

```bash
cd frontend/

# Linting
npm run lint

# Formatting
npm run format

# Type checking
npm run type-check

# Dependency audit
npm audit

# Bundle analysis
npm run analyze
```

### 4. VS Code Configuration

Create `.vscode/settings.json`:

```json
{
  "python.defaultInterpreterPath": "./backend/.venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": false,
  "python.linting.ruffEnabled": true,
  "python.formatting.provider": "black",
  "typescript.preferences.importModuleSpecifier": "relative",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  }
}
```

Create `.vscode/extensions.json`:

```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.black-formatter",
    "charliermarsh.ruff",
    "ms-vscode.vscode-typescript-next",
    "bradlc.vscode-tailwindcss",
    "ms-vscode.vscode-json"
  ]
}
```

## Troubleshooting

### Common Issues

#### 1. Port Already in Use

```bash
# Find process using port
lsof -i :8000
lsof -i :3000

# Kill process
kill -9 <PID>

# Or use different ports
uvicorn app.main:app --port 8001
npm run dev -- --port 3001
```

#### 2. Database Connection Issues

```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check database logs
docker-compose logs postgres

# Reset database
docker-compose down postgres
docker volume rm kairos_postgres_data
docker-compose up -d postgres
```

#### 3. Poetry/Node Dependencies

```bash
# Reset Poetry environment
cd backend/
poetry env remove python
poetry install

# Reset Node modules
cd frontend/
rm -rf node_modules package-lock.json
npm install
```

#### 4. Docker Issues

```bash
# Clean Docker system
docker system prune -a

# Reset Docker Compose
docker-compose down -v
docker-compose up -d

# View container logs
docker-compose logs <service-name>
```

### Debug Mode

#### Backend Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Run with debugger
poetry run python -m debugpy --listen 5678 --wait-for-client -m uvicorn app.main:app --reload
```

#### Frontend Debug Mode

```bash
# Enable debug mode
export NODE_ENV=development
export DEBUG=true

# Run with inspector
node --inspect-brk=0.0.0.0:9229 node_modules/.bin/next dev
```

## Advanced Configuration

### 1. Environment-Specific Settings

#### Development Environment
```bash
# .env.development
DEBUG=true
LOG_LEVEL=DEBUG
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
DATABASE_URL=postgresql+asyncpg://kairos_user:kairos_password@localhost:5432/kairos_bcp_dev
```

#### Testing Environment
```bash
# .env.test
DEBUG=true
LOG_LEVEL=INFO
DATABASE_URL=postgresql+asyncpg://kairos_user:kairos_password@localhost:5432/kairos_bcp_test
```

### 2. Performance Optimization

#### Backend Optimization
```bash
# Enable async profiling
pip install py-spy
py-spy record -o profile.svg -- python -m uvicorn app.main:app

# Memory profiling
pip install memory-profiler
python -m memory_profiler app/main.py
```

#### Frontend Optimization
```bash
# Bundle analysis
npm run build
npm run analyze

# Performance monitoring
npm install --save-dev @next/bundle-analyzer
```

### 3. Security Configuration

#### Backend Security
```bash
# Generate secure secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Enable HTTPS in development
uvicorn app.main:app --ssl-keyfile=key.pem --ssl-certfile=cert.pem
```

#### Frontend Security
```bash
# Content Security Policy
# Configure in next.config.js
```

### 4. Monitoring and Logging

#### Application Monitoring
```bash
# Add monitoring endpoints
# /health - Health check
# /metrics - Prometheus metrics
# /status - System status
```

#### Log Analysis
```bash
# View application logs
tail -f backend/logs/app.log

# Docker logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

## Quick Start Checklist

- [ ] Install prerequisites (Git, Docker, Python, Node.js)
- [ ] Clone repository and create development branch
- [ ] Copy and configure environment files
- [ ] Start infrastructure services with Docker Compose
- [ ] Set up backend environment with Poetry
- [ ] Run database migrations
- [ ] Set up frontend environment with npm
- [ ] Start development servers
- [ ] Verify all services are running
- [ ] Run initial tests
- [ ] Configure IDE with recommended extensions
- [ ] Set up pre-commit hooks

## Support and Resources

### Documentation
- [API Documentation](./API_DOCUMENTATION.md)
- [Deployment Guide](./DEPLOYMENT_GUIDE.md)
- [User Manual](./USER_MANUAL.md)
- [Architecture Documentation](./ARCHITECTURE_ANALYSIS.md)

### Community
- GitHub Issues: Report bugs and request features
- Development Chat: Join our Discord/Slack
- Code Reviews: Participate in pull request reviews
- Wiki: Contribute to documentation

### Additional Resources
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Docker Documentation](https://docs.docker.com/)

---

Happy coding! 🚀

For questions or issues, please open a GitHub issue or contact the development team.