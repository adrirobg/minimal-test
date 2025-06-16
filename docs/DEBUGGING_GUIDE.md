# WSL Debugging Guide for Kairos BCP

**WSL-optimized debugging tips for common development issues.**

This guide covers debugging in the WSL environment with optimal performance and tooling.

## 🐛 Quick WSL Debug Commands

### Check Service Status
```bash
# Ensure you're in WSL native file system
cd ~/projects/kairos-bcp

# See what's running
docker-compose ps

# Check logs for specific service
docker-compose logs backend
docker-compose logs frontend
docker-compose logs postgres

# Follow logs in real-time (use VS Code integrated terminal)
docker-compose logs -f backend
```

### Restart Services
```bash
# Restart specific service
docker-compose restart backend
docker-compose restart frontend

# Restart everything
docker-compose down && docker-compose up -d
```

### Database Issues
```bash
# Connect to database directly
docker-compose exec postgres psql -U kairos_user -d kairos_bcp_dev

# Check database is ready
docker-compose exec postgres pg_isready -U kairos_user

# Reset database completely
docker-compose down -v
docker-compose up -d
```

## 🔍 Common Issues & Solutions

### Backend Not Starting
```bash
# Check Python logs
docker-compose logs backend

# Check if dependencies installed
docker-compose exec backend pip list

# Rebuild backend container
docker-compose build backend
docker-compose up -d backend
```

### Frontend Not Loading
```bash
# Check Node.js logs
docker-compose logs frontend

# Check if packages installed
docker-compose exec frontend npm list

# Rebuild frontend container
docker-compose build frontend
docker-compose up -d frontend
```

### Database Connection Failed
```bash
# Verify PostgreSQL is running
docker-compose ps postgres

# Check database logs
docker-compose logs postgres

# Test connection
docker-compose exec backend python -c "
from app.core.database import engine
print('Database connection OK')
"
```

### Port Already in Use
```bash
# Kill processes on ports
sudo lsof -i :3000 -i :8000 -i :5432 -i :8080
sudo kill -9 <PID>

# Or use different ports in docker-compose.yml
```

## 🔧 WSL Local Development Debug

### Backend Local Debug in WSL
```bash
# Use WSL terminal or VS Code integrated terminal
cd ~/projects/kairos-bcp/backend/
poetry install
poetry shell

# Run with debug mode (better performance in WSL)
uvicorn app.main:app --reload --log-level debug --host 0.0.0.0

# Run specific script
python init_db.py
python sample_data.py

# Use WSL native Python for better performance
which python  # Should show WSL path, not Windows
```

### Frontend Local Debug in WSL
```bash
cd ~/projects/kairos-bcp/frontend/
npm install

# Run with debug (use WSL Node.js)
npm run dev

# Build locally (faster in WSL)
npm run build

# Use WSL native Node.js
which node  # Should show WSL path: /home/user/.nvm/...
```

### VS Code WSL Debugging
```bash
# Open project in VS Code WSL mode
code ~/projects/kairos-bcp

# Use pre-configured debug configurations:
# - Python: FastAPI Backend
# - Node.js: Next.js Frontend  
# - Full Stack: Backend + Frontend

# Set breakpoints and press F5 to start debugging
```

## 📊 Performance Issues

### Slow Database Queries
```bash
# Connect to pgAdmin: http://localhost:8080
# Use Query Tool to analyze slow queries
# Check execution plans with EXPLAIN ANALYZE
```

### High Memory Usage
```bash
# Check container memory usage
docker stats

# Limit container memory in docker-compose.yml
# Add: mem_limit: 512m
```

### Container Won't Start
```bash
# Check Docker disk space
docker system df

# Clean up unused containers/images
docker system prune -a

# Rebuild from scratch
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

## 🚨 Emergency Reset

### Complete Environment Reset
```bash
# Stop everything
docker-compose down -v

# Remove all containers and images
docker system prune -a

# Start fresh
docker-compose up -d --build
```

### Reset Database Only
```bash
# Keep code, reset database
docker-compose down postgres
docker volume rm kairos-bcp_postgres_data
docker-compose up -d postgres
```

## 📝 Debugging Tips

### Enable Verbose Logging
```bash
# Add to docker-compose.yml environment:
LOG_LEVEL: DEBUG

# Or temporarily:
docker-compose exec backend bash
export LOG_LEVEL=DEBUG
```

### Interactive Container Access
```bash
# Access backend container
docker-compose exec backend bash

# Access frontend container
docker-compose exec frontend sh

# Access database
docker-compose exec postgres psql -U kairos_user -d kairos_bcp_dev
```

### Quick Health Checks
```bash
# Test all endpoints
curl http://localhost:8000/health
curl http://localhost:8000/docs
curl http://localhost:3000
curl http://localhost:8080

# Check internal container networking
docker-compose exec backend ping postgres
docker-compose exec frontend ping backend
```