# WSL Troubleshooting Guide for Kairos BCP

Comprehensive troubleshooting guide for common WSL development issues.

## 🚨 Emergency Quick Fixes

### WSL Not Starting
```bash
# Restart WSL completely
wsl.exe --shutdown
# Wait 10 seconds, then start WSL again
wsl.exe

# If still not working, restart Windows Terminal
```

### Project Not Accessible
```bash
# Check if you're in the right location
pwd
# Should show: /home/username/projects/kairos-bcp

# If in Windows file system, migrate:
cp -r /mnt/c/Users/YourName/Projects/kairos-bcp ~/projects/
cd ~/projects/kairos-bcp
```

### VS Code Not in WSL Mode
```bash
# Check bottom-left corner of VS Code
# Should show "WSL: Ubuntu"

# If not, press Ctrl+Shift+P
# Type: "Remote-WSL: Reopen Folder in WSL"
```

## 🔧 Installation Issues

### WSL Installation Failed
```powershell
# Run as Administrator in PowerShell

# Enable WSL feature
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart

# Enable Virtual Machine Platform
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

# Restart Windows, then:
wsl --set-default-version 2

# Install Ubuntu from Microsoft Store
```

### Ubuntu Won't Start
```bash
# Check WSL status
wsl --list --verbose

# If showing "Stopped", start it:
wsl --distribution Ubuntu

# If corrupted, reset Ubuntu:
wsl --unregister Ubuntu
# Then reinstall from Microsoft Store
```

### Permission Denied Errors
```bash
# Fix common permission issues
sudo chown -R $USER:$USER ~/projects/
chmod +x ~/projects/kairos-bcp/scripts/*.sh

# If Docker permission issues:
sudo usermod -aG docker $USER
newgrp docker
```

## 🐳 Docker Integration Issues

### Docker Daemon Not Running
```bash
# Start Docker service
sudo service docker start

# Enable Docker auto-start
sudo systemctl enable docker

# If Docker Desktop conflicts:
# Uninstall Docker Desktop from Windows
# Use Docker only in WSL
```

### Docker Compose Command Not Found
```bash
# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker-compose --version
```

### Docker Images Won't Build
```bash
# Check disk space
df -h
docker system df

# Clean up if needed
docker system prune -a

# Increase WSL memory (C:\Users\%USERNAME%\.wslconfig):
[wsl2]
memory=8GB
processors=4

# Restart WSL after config change
wsl.exe --shutdown
```

## 🌐 Network and Port Issues

### Localhost Not Accessible from Windows
```bash
# Use localhost, not 127.0.0.1
# ✅ http://localhost:3000
# ❌ http://127.0.0.1:3000

# Check port forwarding
netstat -tulpn | grep :3000

# If needed, manually forward ports (PowerShell as Admin):
netsh interface portproxy add v4tov4 listenport=3000 listenaddress=0.0.0.0 connectport=3000 connectaddress=127.0.0.1
```

### Port Already in Use
```bash
# Find process using port
sudo lsof -i :3000
sudo lsof -i :8000

# Kill process
sudo kill -9 <PID>

# Or use different ports in development
npm run dev -- --port 3001
uvicorn app.main:app --port 8001
```

### DNS Resolution Issues
```bash
# Check DNS resolution
nslookup google.com

# If failing, update DNS servers
sudo tee /etc/systemd/resolved.conf > /dev/null <<EOF
[Resolve]
DNS=1.1.1.1 8.8.8.8
FallbackDNS=1.0.0.1 8.8.4.4
EOF

sudo systemctl restart systemd-resolved
```

## 📁 File System Issues

### Slow File Operations
```bash
# Verify you're in WSL native file system
pwd
# Should start with /home/, not /mnt/c/

# If in Windows file system, migrate:
rsync -av --progress /mnt/c/path/to/project/ ~/projects/new-location/

# Check file system performance
time ls -la | wc -l
```

### File Permissions Broken
```bash
# Fix ownership
sudo chown -R $USER:$USER ~/projects/kairos-bcp/

# Fix script permissions
find ~/projects/kairos-bcp/scripts/ -name "*.sh" -exec chmod +x {} \;

# Fix directory permissions
find ~/projects/kairos-bcp/ -type d -exec chmod 755 {} \;
find ~/projects/kairos-bcp/ -type f -exec chmod 644 {} \;
```

### Can't Edit Files
```bash
# Check if files are read-only
ls -la problematic-file

# Remove read-only attribute
chmod 644 problematic-file

# If VS Code can't save files, check WSL permissions
code --version
# Ensure VS Code is running in WSL mode
```

## 🛠️ Development Tools Issues

### Command Not Found Errors
```bash
# Reload shell configuration
source ~/.bashrc

# Check PATH
echo $PATH

# If tools missing, reinstall:
# Node.js
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.bashrc
nvm install --lts

# Poetry
curl -sSL https://install.python-poetry.org | python3 -
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Python/Poetry Issues
```bash
# Check Python installation
python3 --version
which python3

# If Poetry not working
poetry --version

# Reset Poetry environment
cd ~/projects/kairos-bcp/backend/
poetry env remove python
poetry install

# If pip issues
python3 -m pip install --upgrade pip
```

### Node.js/NPM Issues
```bash
# Check Node.js installation
node --version
npm --version
which node

# If node command not found
nvm use --lts
nvm alias default node

# Clear npm cache
npm cache clean --force

# Reset node_modules
rm -rf node_modules package-lock.json
npm install
```

## 🖥️ VS Code Issues

### Extensions Not Working
```bash
# Ensure you're in WSL mode
# Bottom-left should show "WSL: Ubuntu"

# If extensions aren't loading:
# 1. Press Ctrl+Shift+P
# 2. Type: "Developer: Reload Window"

# If still not working, reinstall extensions in WSL context
```

### Debugger Not Working
```bash
# Check debug configuration exists
ls .vscode/launch.json

# Verify Python interpreter path
# Press Ctrl+Shift+P
# Type: "Python: Select Interpreter"
# Select: ~/projects/kairos-bcp/backend/.venv/bin/python

# Check if debugpy is installed
cd backend/
poetry run pip list | grep debugpy
```

### IntelliSense Not Working
```bash
# For Python IntelliSense
cd backend/
poetry shell
# Then restart VS Code

# For TypeScript IntelliSense
cd frontend/
npm install
# Then restart VS Code

# If still not working, check TypeScript version
npm list typescript
```

## 💾 Memory and Performance Issues

### Out of Memory Errors
```bash
# Check WSL memory usage
free -h

# Check Windows Task Manager for "Vmmem" process

# Increase WSL memory limit
# Edit C:\Users\%USERNAME%\.wslconfig:
[wsl2]
memory=8GB
swap=2GB

# Restart WSL
wsl.exe --shutdown
```

### Slow Performance
```bash
# Check if Windows Defender is scanning WSL files
# Add exclusions in Windows Security:
# - WSL distribution path
# - Docker data directory

# Check disk usage
df -h
du -sh ~/projects/kairos-bcp/

# Clean up unnecessary files
docker system prune -a
npm cache clean --force
poetry cache clear . --all
```

### High CPU Usage
```bash
# Check what's using CPU
htop

# If Docker containers using too much CPU
docker stats

# Limit container resources in docker-compose.yml:
services:
  backend:
    cpus: "0.5"
    mem_limit: 512m
```

## 🔄 Environment Reset Procedures

### Quick Environment Reset
```bash
# Stop all services
docker-compose down

# Clear Docker resources
docker system prune -a

# Restart development environment
docker-compose up -d
```

### Complete WSL Reset
```bash
# Export current environment (backup)
wsl --export Ubuntu ubuntu-backup.tar

# Reset WSL distribution
wsl --unregister Ubuntu

# Reinstall Ubuntu from Microsoft Store
# Then restore project from backup or re-clone
```

### Project-Only Reset
```bash
# Keep WSL, reset only project
cd ~/projects/
rm -rf kairos-bcp/

# Re-clone and setup
git clone <repo-url> kairos-bcp
cd kairos-bcp/
# Follow setup instructions
```

## 📋 Diagnostic Commands

### System Information
```bash
# WSL version and distribution info
wsl --list --verbose
cat /etc/os-release

# System resources
free -h
df -h
lscpu

# Network configuration
ip addr show
cat /etc/resolv.conf
```

### Docker Diagnostics
```bash
# Docker system info
docker --version
docker info
docker system df

# Container status
docker ps -a
docker-compose ps

# Network info
docker network ls
```

### Development Environment Check
```bash
# Tool versions
node --version
npm --version
python3 --version
poetry --version
git --version

# Project structure check
ls -la ~/projects/kairos-bcp/
```

## 🆘 When All Else Fails

### Contact Support Checklist
Before seeking help, gather this information:

```bash
# System info
wsl --list --verbose > system-info.txt
cat /etc/os-release >> system-info.txt
free -h >> system-info.txt

# Error logs
docker-compose logs > docker-logs.txt
# VS Code logs: Help → Developer Tools → Console

# Configuration files
cat ~/.bashrc > config-backup.txt
cat ~/.wslconfig >> config-backup.txt  # If exists
```

### Complete Fresh Start
If everything is broken and you need to start over:

1. **Backup important data**
2. **Reset WSL**: `wsl --unregister Ubuntu`
3. **Reinstall Ubuntu** from Microsoft Store
4. **Follow [WSL Quick Start Guide](WSL_QUICK_START.md)**
5. **Re-clone project** to `~/projects/`

This troubleshooting guide covers 95% of common WSL development issues. For WSL-specific Docker and performance debugging, see the dedicated guides.