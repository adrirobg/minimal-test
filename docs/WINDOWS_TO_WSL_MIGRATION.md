# Windows to WSL Migration Guide for Kairos BCP

Migrate your existing Windows development setup to WSL for better performance and consistency.

## Why Migrate to WSL?

### Performance Benefits
- **10x faster file operations** in WSL native file system
- **Better Docker performance** without Docker Desktop overhead
- **Faster npm/pip installs** with native Linux package management
- **Reduced antivirus interference** with development tools

### Development Benefits
- **Consistent environment** with production/deployment
- **Better shell scripting** with native bash/zsh
- **Superior package management** with apt/snap
- **No PATH pollution** from Windows tools

### Tool Integration
- **Seamless VS Code integration** with Remote-WSL
- **Native Docker support** without Windows compatibility layers
- **Better Git performance** with Linux file system
- **Terminal multiplexing** with tmux/screen

## Pre-Migration Checklist

### Backup Current Setup
```powershell
# 1. Export VS Code settings
# File → Preferences → Settings → ... → Export Settings

# 2. Document current VS Code extensions
code --list-extensions > vscode-extensions-backup.txt

# 3. Backup project files (if in Windows file system)
# Copy your project to a safe location

# 4. Document current environment variables
# Note any custom PATH additions, API keys, etc.
```

### Inventory Current Tools
```powershell
# Document currently installed tools:
node --version
npm --version
python --version
pip --version
git --version
docker --version
```

## Migration Process

### Step 1: Install WSL
Follow the [WSL Quick Start Guide](WSL_QUICK_START.md) for installation.

### Step 2: Project Migration

#### Option A: Fresh Setup (Recommended)
```bash
# 1. Clone project directly in WSL
cd ~/projects
git clone <repository-url> kairos-bcp

# 2. Install dependencies fresh
cd kairos-bcp/backend
poetry install

cd ../frontend  
npm install
```

#### Option B: Copy Existing Project
```bash
# 1. Copy from Windows to WSL (one-time operation)
cp -r /mnt/c/Users/YourUsername/Projects/kairos-bcp ~/projects/

# 2. Clean up Windows-specific artifacts
cd ~/projects/kairos-bcp
rm -rf backend/.venv frontend/node_modules
rm -rf backend/__pycache__ backend/.pytest_cache
rm -rf frontend/.next

# 3. Reinstall dependencies
cd backend && poetry install
cd ../frontend && npm install
```

### Step 3: VS Code Migration

```bash
# 1. Install Remote-WSL extension in your existing VS Code
# 2. Open project in WSL mode
cd ~/projects/kairos-bcp
code .

# 3. Install recommended extensions when prompted
# All extensions will be installed in WSL context
```

### Step 4: Environment Variables

```bash
# 1. Recreate environment variables in WSL
# Add to ~/.bashrc or ~/.zshrc

# Example:
echo 'export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/kairos_bcp"' >> ~/.bashrc
echo 'export NEXT_PUBLIC_API_URL="http://localhost:8000"' >> ~/.bashrc
source ~/.bashrc
```

### Step 5: Tool Configuration

```bash
# 1. Git configuration
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
git config --global core.editor "code --wait"

# 2. SSH keys (if using GitHub/GitLab)
# Copy from Windows or generate new ones
ssh-keygen -t ed25519 -C "your.email@example.com"

# 3. Database connections
# Update connection strings to use localhost instead of Windows IPs
```

## Troubleshooting Migration Issues

### File Permission Issues
```bash
# Fix ownership after copying from Windows
sudo chown -R $USER:$USER ~/projects/kairos-bcp

# Fix execute permissions on scripts
chmod +x scripts/*.sh
```

### Path Issues
```bash
# If tools are not found, check PATH
echo $PATH

# Add missing paths to ~/.bashrc
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Docker Issues
```bash
# Ensure Docker daemon is running
sudo service docker start

# Add user to docker group if needed
sudo usermod -aG docker $USER
newgrp docker
```

### Port Access Issues
```bash
# Use localhost instead of 127.0.0.1 for Windows access
# ✅ http://localhost:3000
# ❌ http://127.0.0.1:3000

# Check Windows firewall if ports are blocked
```

## Performance Comparison

### Before (Windows)
```bash
# Typical performance on Windows:
npm install        # ~60-120 seconds
pytest             # ~30-45 seconds  
docker build       # ~300-600 seconds
File search (rg)   # ~2-5 seconds
```

### After (WSL)
```bash
# Expected performance in WSL:
npm install        # ~15-30 seconds
pytest             # ~10-20 seconds
docker build       # ~60-120 seconds
File search (rg)   # ~0.5-1 seconds
```

## Feature Comparison

| Feature | Windows | WSL | Notes |
|---------|---------|-----|-------|
| File Operations | Slow | Fast | 10x faster in WSL |
| Docker | Docker Desktop | Native | Better performance |
| Shell Scripting | PowerShell/Git Bash | Bash/Zsh | Native Linux tools |
| Package Management | Chocolatey/winget | apt/snap | More reliable |
| Development Servers | Good | Excellent | Better file watching |
| VS Code Integration | Native | Remote-WSL | Same experience |
| Database Access | Good | Excellent | Better PostgreSQL tools |
| Git Performance | Good | Excellent | Faster operations |

## Common Migration Pitfalls

### 1. Working in Windows File System
```bash
# ❌ Don't work here (slow)
cd /mnt/c/Users/Username/Projects/

# ✅ Work here instead (fast)  
cd ~/projects/
```

### 2. Mixing Windows and WSL Tools
```bash
# ❌ Don't mix environments
/mnt/c/Program\ Files/nodejs/npm install  # Windows npm in WSL

# ✅ Use consistent toolchain
npm install  # WSL npm
```

### 3. Forgetting to Update Scripts
```bash
# Update any hardcoded Windows paths in scripts
# Change C:\Users\... to /home/username/...
# Update PowerShell scripts to bash scripts
```

### 4. Environment Variable Confusion
```bash
# Windows environment variables don't carry over
# Recreate necessary variables in ~/.bashrc
```

## Migration Validation

### 1. Performance Test
```bash
# Test file operations speed
time find . -name "*.py" | wc -l
time grep -r "function" . | wc -l

# Should be significantly faster than Windows
```

### 2. Development Workflow Test
```bash
# Start full development environment
docker-compose up -d
cd backend && poetry shell
cd ../frontend && npm run dev

# All should start without errors
```

### 3. VS Code Integration Test
```bash
# Open in VS Code
code .

# Verify:
# - Extensions load properly
# - Debugging works
# - Terminal is WSL
# - IntelliSense functions
```

## Rollback Plan (If Needed)

If you need to return to Windows development:

```bash
# 1. Copy project back to Windows
cp -r ~/projects/kairos-bcp /mnt/c/Users/YourUsername/Projects/

# 2. Reinstall dependencies in Windows
# 3. Reconfigure VS Code for Windows development
# 4. Update environment variables
```

## Post-Migration Optimization

### 1. WSL Configuration
```bash
# Create/update C:\Users\%USERNAME%\.wslconfig
[wsl2]
memory=8GB
processors=4
swap=2GB
```

### 2. Windows Defender Exclusions
Add these folders to Windows Defender exclusions:
- `%USERPROFILE%\AppData\Local\Docker`
- `%LOCALAPPDATA%\Packages\CanonicalGroupLimited*`

### 3. Install Additional Tools
```bash
# Enhanced shell
sudo apt install zsh
sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"

# Better terminal multiplexer
sudo apt install tmux

# Advanced file operations
sudo apt install ripgrep fd-find bat exa
```

## Success Metrics

You've successfully migrated when:

- ✅ All development commands run faster
- ✅ File operations are noticeably quicker
- ✅ Docker operations complete without Docker Desktop
- ✅ VS Code works seamlessly with WSL
- ✅ No Windows-specific path issues
- ✅ Database connections work without configuration changes
- ✅ All tests pass in the new environment
- ✅ Development workflow is simpler

**Migration typically takes 30-60 minutes and provides immediate performance benefits.**

Welcome to the faster, more consistent world of WSL development!