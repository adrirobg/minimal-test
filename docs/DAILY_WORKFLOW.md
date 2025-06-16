# Daily Development Workflow

**Optimized daily routine for productive personal development.**

## ☀️ Morning Startup (2 minutes)

### 1. Start Development Environment
```bash
# Navigate to project
cd kairos-bcp

# Start all services
docker-compose up -d

# Wait for services (30-60 seconds)
# ☕ Perfect time for coffee!
```

### 2. Verify Everything is Running
```bash
# Quick status check
docker-compose ps

# Should see: postgres, pgadmin, backend, frontend all "Up"
```

### 3. Open Development URLs
- **📱 Frontend**: http://localhost:3000
- **🔧 Backend API**: http://localhost:8000/docs
- **💾 Database**: http://localhost:8080 (pgAdmin)

## 💻 Active Development

### Code Editing Workflow
```bash
# Open your favorite editor
code .                    # VS Code
vim backend/app/          # Vim
nano frontend/src/        # Nano
```

### Hot-Reload Development
- **Backend**: Edit `backend/app/*.py` → Auto-reloads ⚡
- **Frontend**: Edit `frontend/src/*.tsx` → Auto-reloads ⚡
- **Database**: Changes via pgAdmin or migrations

### Real-time Monitoring
```bash
# Watch logs in separate terminal
docker-compose logs -f backend frontend

# Or specific service
docker-compose logs -f backend
```

## 🧪 Testing Changes

### Quick Verification
```bash
# Test backend API
curl http://localhost:8000/health

# Test frontend loading
curl -I http://localhost:3000

# Database connection
docker-compose exec postgres pg_isready -U kairos_user
```

### Feature Testing
1. **Make changes** in your editor
2. **Save files** (auto-reload triggers)
3. **Check browser** for frontend changes
4. **Check API docs** at http://localhost:8000/docs for backend

## 📊 Database Work

### Quick Database Access
```bash
# Open pgAdmin: http://localhost:8080
# Login: admin@kairos.dev / admin
# Server: Already configured!
```

### Command Line Database
```bash
# Direct SQL access
docker-compose exec postgres psql -U kairos_user -d kairos_bcp_dev

# Run migrations
docker-compose exec backend alembic upgrade head

# Create sample data
docker-compose exec backend python sample_data.py
```

## 🔄 Git Workflow

### Daily Git Routine
```bash
# Start of day
git pull origin main

# Create feature branch
git checkout -b feature/my-new-feature

# Make commits frequently
git add .
git commit -m "Add user authentication"

# Push when ready
git push origin feature/my-new-feature
```

## 🛠️ Common Daily Tasks

### Add New API Endpoint
1. **Edit**: `backend/app/api/v1/new_endpoint.py`
2. **Test**: http://localhost:8000/docs
3. **Frontend**: Connect from `frontend/src/`

### Add New Page
1. **Create**: `frontend/src/app/new-page/page.tsx`
2. **View**: http://localhost:3000/new-page
3. **Style**: Edit with Tailwind CSS

### Database Schema Changes
1. **Edit**: `backend/app/models/`
2. **Migrate**: `docker-compose exec backend alembic revision --autogenerate -m "Description"`
3. **Apply**: `docker-compose exec backend alembic upgrade head`

## 🌙 End of Day (1 minute)

### Save Your Work
```bash
# Commit your changes
git add .
git commit -m "End of day: working on feature X"
git push origin feature/my-branch
```

### Shutdown (Optional)
```bash
# Stop services (saves computer resources)
docker-compose down

# Or leave running for tomorrow
# (faster startup, uses more resources)
```

## ⚡ Productivity Tips

### Terminal Shortcuts
```bash
# Add to ~/.bashrc or ~/.zshrc
alias kup="docker-compose up -d"
alias kdown="docker-compose down"
alias klogs="docker-compose logs -f"
alias kps="docker-compose ps"
alias krestart="docker-compose restart"

# Quick project navigation
alias kcd="cd ~/path/to/kairos-bcp"
```

### VS Code Setup
```bash
# Recommended extensions
code --install-extension ms-python.python
code --install-extension bradlc.vscode-tailwindcss
code --install-extension ms-vscode.vscode-typescript-next
```

### Browser Bookmarks
- 📱 Frontend: http://localhost:3000
- 🔧 API Docs: http://localhost:8000/docs
- 💾 pgAdmin: http://localhost:8080

## 🚨 When Things Go Wrong

### Quick Fixes
```bash
# Restart everything
docker-compose restart

# Fresh start (loses data)
docker-compose down -v && docker-compose up -d

# Check what's wrong
docker-compose logs
```

### Get Help
1. **Check logs**: `docker-compose logs [service]`
2. **Read error messages** carefully
3. **Consult**: [DEBUGGING_GUIDE.md](./DEBUGGING_GUIDE.md)
4. **Reset if stuck**: Complete environment reset

## 📈 Tracking Progress

### Daily Wins
- ✅ New features implemented
- ✅ Bugs fixed
- ✅ Code improvements
- ✅ Learning achieved

### Weekly Review
- Review git commits
- Check API documentation
- Update personal notes
- Plan next week's features

---

**Remember**: The goal is **consistent daily progress**, not perfection! 🎯