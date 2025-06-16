# Troubleshooting Guide

**Quick solutions for common development problems.**

## 🚀 Quick Fixes (Try These First)

### The Universal Fix
```bash
# Stop everything and start fresh
docker-compose down -v
docker-compose up -d

# Wait 60 seconds, then test
curl http://localhost:8000/health
```

### Service-Specific Restart
```bash
# Restart just one service
docker-compose restart backend
docker-compose restart frontend
docker-compose restart postgres
```

### Check What's Running
```bash
# See service status
docker-compose ps

# Check logs for errors
docker-compose logs backend
docker-compose logs frontend
```

## 🔧 Common Problems & Solutions

### Problem: Services Won't Start

**Symptoms**: `docker-compose up` fails or containers exit immediately

**Solutions**:
```bash
# Check Docker is running
docker version

# Check disk space
docker system df
df -h

# Clean up if needed
docker system prune -a

# Rebuild containers
docker-compose build --no-cache
docker-compose up -d
```

### Problem: Port Already in Use

**Symptoms**: Error about port 3000, 8000, 5432, or 8080 already in use

**Solutions**:
```bash
# Find what's using the port
sudo lsof -i :3000
sudo lsof -i :8000
sudo lsof -i :5432
sudo lsof -i :8080

# Kill the process
sudo kill -9 <PID>

# Or change ports in docker-compose.yml
# Change "3000:3000" to "3001:3000"
```

### Problem: Database Connection Failed

**Symptoms**: Backend can't connect to PostgreSQL

**Solutions**:
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check PostgreSQL logs
docker-compose logs postgres

# Wait longer (database takes time to start)
sleep 30

# Test connection manually
docker-compose exec postgres pg_isready -U kairos_user

# Reset database
docker-compose down postgres
docker volume rm $(docker volume ls -q | grep postgres)
docker-compose up -d postgres
```

### Problem: Hot-Reload Not Working

**Symptoms**: Code changes don't automatically refresh

**Backend Solutions**:
```bash
# Check backend logs
docker-compose logs backend

# Restart backend
docker-compose restart backend

# Check file mounting
docker-compose exec backend ls -la /app
```

**Frontend Solutions**:
```bash
# Check frontend logs  
docker-compose logs frontend

# Restart frontend
docker-compose restart frontend

# Clear Next.js cache
docker-compose exec frontend rm -rf .next
docker-compose restart frontend
```

### Problem: pgAdmin Won't Load

**Symptoms**: http://localhost:8080 doesn't work

**Solutions**:
```bash
# Check pgAdmin is running
docker-compose ps pgadmin

# Check pgAdmin logs
docker-compose logs pgadmin

# Wait longer (pgAdmin takes time to start)
sleep 60

# Try different browser or incognito mode
# Clear browser cache

# Restart pgAdmin
docker-compose restart pgadmin
```

## 💾 Database Issues

### Database Won't Start
```bash
# Check disk space
df -h

# Check PostgreSQL logs
docker-compose logs postgres

# Remove and recreate database
docker-compose down postgres
docker volume rm $(docker volume ls -q | grep postgres)
docker-compose up -d postgres
```

### Can't Connect to Database
```bash
# Wait for database to be ready
docker-compose exec postgres pg_isready -U kairos_user -d kairos_bcp_dev

# Check connection from backend
docker-compose exec backend python -c "
from app.core.database import engine
import asyncio
asyncio.run(engine.dispose())
print('Database connection test OK')
"
```

### Migrations Failing
```bash
# Check current migration state
docker-compose exec backend alembic current

# Reset migrations (DESTRUCTIVE - loses data)
docker-compose exec backend alembic downgrade base
docker-compose exec backend alembic upgrade head

# Create fresh database
docker-compose down postgres
docker volume rm $(docker volume ls -q | grep postgres)
docker-compose up -d postgres
docker-compose exec backend alembic upgrade head
```

## 🌐 Network Issues

### Services Can't Talk to Each Other
```bash
# Check Docker networks
docker network ls

# Test internal connectivity
docker-compose exec backend ping postgres
docker-compose exec frontend ping backend

# Restart networking
docker-compose down
docker-compose up -d
```

### Frontend Can't Reach Backend
```bash
# Check backend is accessible
curl http://localhost:8000/health

# Check frontend environment
docker-compose exec frontend env | grep API_URL

# Check CORS settings in backend
# Edit backend/app/main.py CORS configuration
```

## 🐛 Performance Issues

### Services Running Slowly
```bash
# Check resource usage
docker stats

# Check disk space
df -h
docker system df

# Clean up unused resources
docker system prune -a

# Allocate more memory to Docker Desktop
# (Increase in Docker Desktop settings)
```

### Database Queries Slow
```bash
# Connect to pgAdmin: http://localhost:8080
# Use Query Tool to analyze slow queries
# Run: EXPLAIN ANALYZE SELECT ...

# Check database size
docker-compose exec postgres psql -U kairos_user -d kairos_bcp_dev -c "
SELECT pg_size_pretty(pg_database_size('kairos_bcp_dev'));
"
```

## 🖥️ Platform-Specific Issues

### Windows Issues
```bash
# Use WSL2 for better performance
wsl --set-default-version 2

# Check Docker Desktop is using WSL2 backend
# (Settings > General > Use WSL2 based engine)

# File watching issues in WSL2
# Add to docker-compose.yml:
# environment:
#   - WATCHPACK_POLLING=true
```

### macOS Issues
```bash
# File sharing performance
# Add project directory to Docker Desktop file sharing
# (Settings > Resources > File Sharing)

# Permission issues
sudo chown -R $(whoami) .
```

### Linux Issues
```bash
# User not in docker group
sudo usermod -aG docker $USER
newgrp docker

# Firewall blocking ports
sudo ufw allow 3000
sudo ufw allow 8000
sudo ufw allow 5432
sudo ufw allow 8080
```

## 📱 Browser Issues

### Frontend Not Loading
```bash
# Clear browser cache
# Try incognito/private mode
# Try different browser

# Check frontend container
docker-compose logs frontend

# Check if Next.js compiled successfully
docker-compose exec frontend ls -la .next
```

### API Docs Not Working
```bash
# Check backend is running
curl http://localhost:8000/health

# Clear browser cache
# Try: http://localhost:8000/docs

# Check backend logs
docker-compose logs backend
```

## 🆘 Emergency Procedures

### Complete Environment Reset
```bash
# NUCLEAR OPTION - Destroys all data!
docker-compose down -v
docker system prune -a
docker volume prune
docker network prune

# Start fresh
docker-compose up -d --build

# Wait for everything to start
sleep 120

# Test basic functionality
curl http://localhost:8000/health
curl -I http://localhost:3000
```

### Partial Reset (Keep Database)
```bash
# Keep database, restart everything else
docker-compose down
docker-compose up -d
```

### Reset Database Only
```bash
# Keep code, reset database
docker-compose down postgres
docker volume rm $(docker volume ls -q | grep postgres)
docker-compose up -d postgres

# Apply migrations and sample data
sleep 30
docker-compose exec backend alembic upgrade head
docker-compose exec backend python sample_data.py
```

## 📞 Getting Help

### Collect Debug Information
```bash
# System information
docker version
docker-compose version
uname -a

# Service status
docker-compose ps

# Recent logs
docker-compose logs --tail=50

# Resource usage
docker stats --no-stream
```

### Before Asking for Help
1. ✅ Try the quick fixes above
2. ✅ Check logs for error messages
3. ✅ Try a complete reset
4. ✅ Note exactly what you were doing when the problem occurred
5. ✅ Include error messages and logs

### Where to Get Help
- 📖 Read error messages carefully
- 🔍 Search issues in project repository
- 📝 Create new issue with debug information
- 💬 Ask in development chat/Discord

---

**Remember**: Most issues are solved by restarting services or resetting the environment! 🔄