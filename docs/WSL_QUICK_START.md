# WSL Quick Start Guide for Kairos BCP Development

Get started with Kairos BCP development on WSL in 15 minutes or less.

## Prerequisites Check

- Windows 10 version 2004+ or Windows 11
- Administrative privileges on Windows
- At least 8GB RAM recommended
- 20GB free disk space

## Step 1: Install WSL (5 minutes)

### Option A: Automatic Installation (Windows 11/Recent Windows 10)

```powershell
# Open PowerShell as Administrator and run:
wsl --install

# This installs WSL 2 + Ubuntu 22.04 LTS automatically
# Restart when prompted
```

### Option B: Manual Installation (Older Windows 10)

```powershell
# 1. Enable WSL feature
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart

# 2. Enable Virtual Machine Platform  
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

# 3. Restart Windows

# 4. Download and install WSL2 Linux kernel update
# Visit: https://wslstorestorage.blob.core.windows.net/wslblob/wsl_update_x64.msi

# 5. Set WSL 2 as default
wsl --set-default-version 2

# 6. Install Ubuntu from Microsoft Store
# Search "Ubuntu 22.04 LTS" in Microsoft Store and install
```

## Step 2: Initial WSL Setup (3 minutes)

```bash
# 1. First launch will prompt for username/password
# Choose a simple username (e.g., your first name)
# Password will be used for sudo operations

# 2. Update system packages
sudo apt update && sudo apt upgrade -y

# 3. Install essential tools
sudo apt install -y curl wget git build-essential
```

## Step 3: Development Tools Installation (5 minutes)

### Install Node.js

```bash
# Install Node Version Manager (nvm)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# Restart terminal or run:
source ~/.bashrc

# Install latest LTS Node.js
nvm install --lts
nvm use --lts

# Verify installation
node --version
npm --version
```

### Install Python and Poetry

```bash
# Python should be pre-installed, but let's ensure we have pip
sudo apt install -y python3 python3-pip python3-venv

# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Verify installation
poetry --version
```

### Install Docker

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER

# Apply group membership
newgrp docker

# Verify installation
docker --version
```

## Step 4: Clone and Setup Kairos BCP (2 minutes)

```bash
# Create projects directory
mkdir -p ~/projects
cd ~/projects

# Clone the repository (replace with actual repo URL)
git clone <repository-url> kairos-bcp
cd kairos-bcp

# Install backend dependencies
cd backend
poetry install
cd ..

# Install frontend dependencies
cd frontend
npm install
cd ..

# Start development services
docker-compose up -d
```

## Step 5: Install and Setup VS Code

```bash
# Install VS Code in Windows if not already installed
# Download from: https://code.visualstudio.com/

# Install Remote-WSL extension
# 1. Open VS Code
# 2. Go to Extensions (Ctrl+Shift+X)
# 3. Search for "Remote - WSL"
# 4. Install the extension by Microsoft

# Open project in VS Code
code .
```

## Verification Checklist

Run these commands to verify everything is working:

```bash
# Check WSL version
wsl --list --verbose
# Should show Ubuntu running WSL 2

# Check Node.js
node --version && npm --version
# Should show v18+ and npm version

# Check Python and Poetry
python3 --version && poetry --version
# Should show Python 3.10+ and Poetry version

# Check Docker
docker --version && docker ps
# Should show Docker version and running containers

# Check project structure
ls -la ~/projects/kairos-bcp/
# Should show backend/, frontend/, docker-compose.yml, etc.

# Test development servers
# Backend: http://localhost:8000
curl http://localhost:8000/health 2>/dev/null || echo "Backend not running yet"

# Frontend: http://localhost:3000  
curl http://localhost:3000 2>/dev/null || echo "Frontend not running yet"

# Database: Check PostgreSQL
docker exec -it postgres psql -U postgres -c "SELECT version();" 2>/dev/null || echo "Database not running yet"
```

## Quick Development Commands

```bash
# Daily startup (run from project root)
docker-compose up -d              # Start services
cd backend && poetry shell        # Activate Python environment
cd ../frontend && npm run dev     # Start frontend (in new terminal)

# Quick tests
cd backend && poetry run pytest   # Run backend tests
cd frontend && npm test           # Run frontend tests

# Code quality
cd backend && poetry run black .  # Format Python code
cd frontend && npm run lint       # Lint frontend code

# Database operations
./scripts/reset-db.sh             # Reset database
./scripts/load-sample-data.sh     # Load sample data
```

## Common First-Time Issues

### Issue: "Command not found" errors
```bash
# Solution: Restart terminal or run
source ~/.bashrc
```

### Issue: Permission denied for Docker
```bash
# Solution: Restart WSL
wsl.exe --shutdown
# Then restart WSL and try again
```

### Issue: Ports not accessible from Windows
```bash
# Solution: Use localhost, not 127.0.0.1
# Windows: http://localhost:3000 ✅
# Windows: http://127.0.0.1:3000 ❌
```

### Issue: VS Code doesn't open in WSL mode
```bash
# Solution: Check bottom-left corner of VS Code
# Should show "WSL: Ubuntu"
# If not, press Ctrl+Shift+P → "Remote-WSL: Reopen Folder in WSL"
```

## Next Steps

1. **Read the full setup guide**: `WSL_DEVELOPMENT_SETUP.md`
2. **Optimize performance**: `WSL_PERFORMANCE_TIPS.md`  
3. **Configure VS Code**: `VSCODE_WSL_SETUP.md`
4. **Learn the development workflow**: `DEVELOPMENT_SETUP.md`
5. **Troubleshooting**: `WSL_TROUBLESHOOTING.md`

## Success Indicators

You'll know everything is working when:

- ✅ VS Code opens the project with "WSL: Ubuntu" in bottom-left
- ✅ All recommended extensions install automatically
- ✅ Backend starts without errors: `cd backend && poetry run uvicorn app.main:app --reload`
- ✅ Frontend starts without errors: `cd frontend && npm run dev`
- ✅ Database is accessible: `docker exec -it postgres psql -U postgres`
- ✅ You can browse to http://localhost:3000 and see the application

**Total setup time: ~15 minutes**

Welcome to WSL-based development! You now have a powerful, consistent development environment that matches production systems and works seamlessly with modern development tools.