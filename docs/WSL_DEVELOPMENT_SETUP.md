# WSL Development Setup for Kairos BCP

This guide optimizes the Kairos BCP development environment specifically for WSL (Windows Subsystem for Linux) on Windows.

## Prerequisites

- Windows 10 version 2004+ or Windows 11
- WSL 2 installed and configured
- Ubuntu 22.04 LTS (recommended distribution)

## WSL Performance Optimization

### 1. File System Optimization

**CRITICAL**: Always work within the WSL file system (`/home/user/`) for optimal performance.

```bash
# ✅ Good - WSL native file system
cd ~/projects/kairos-bcp

# ❌ Avoid - Windows file system (slow)
cd /mnt/c/Users/Username/Projects/kairos-bcp
```

### 2. Memory Configuration

Create or update `/etc/wsl.conf`:

```ini
[wsl2]
memory=8GB
processors=4
swap=2GB
localhostForwarding=true

[boot]
systemd=true

[automount]
enabled=true
options="metadata,uid=1000,gid=1000,umask=22,fmask=11"
```

### 3. Network Optimization

Enable localhost forwarding for seamless development:

```bash
# Add to ~/.bashrc or ~/.zshrc
export WSL_HOST=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}')
export DISPLAY=$WSL_HOST:0.0
```

## Development Environment Setup

### 1. Clone Project in WSL

```bash
# Create projects directory in WSL
mkdir -p ~/projects
cd ~/projects

# Clone the repository
git clone <repository-url> kairos-bcp
cd kairos-bcp
```

### 2. Install Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install essential tools
sudo apt install -y curl wget git build-essential

# Install Node.js (via nvm)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.bashrc
nvm install --lts
nvm use --lts

# Install Python and Poetry
sudo apt install -y python3 python3-pip python3-venv
curl -sSL https://install.python-poetry.org | python3 -
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker
```

### 3. Project Setup

```bash
# Backend setup
cd backend
poetry install
cd ..

# Frontend setup
cd frontend
npm install
cd ..

# Start development services
docker-compose up -d
```

## Performance Best Practices

### 1. Use WSL-native Commands

```bash
# ✅ Use WSL commands
code .                    # Opens VS Code in WSL mode
explorer.exe .           # Opens Windows Explorer from WSL
wsl.exe --shutdown       # Restart WSL if needed
```

### 2. File Watching Optimization

Increase inotify limits for better file watching:

```bash
# Add to /etc/sysctl.conf
echo 'fs.inotify.max_user_watches=524288' | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

### 3. Docker Integration

Use Docker in WSL 2 mode for better performance:

```bash
# Verify Docker is using WSL 2 backend
docker info | grep -i wsl

# Use Docker Compose from WSL
docker-compose up -d
```

## Development Workflow

### 1. Daily Startup

```bash
# Start all services
./scripts/dev-setup.sh

# Or manually:
docker-compose up -d
cd backend && poetry shell
cd ../frontend && npm run dev
```

### 2. Database Operations

```bash
# Reset database
./scripts/reset-db.sh

# Load sample data
./scripts/load-sample-data.sh

# View logs
./scripts/dev-logs.sh
```

### 3. Code Quality

```bash
# Backend quality checks
cd backend
poetry run black .
poetry run ruff check . --fix
poetry run mypy .
poetry run pytest

# Frontend quality checks
cd frontend
npm run lint
npm run type-check
npm run test
```

## Port Forwarding

WSL 2 automatically forwards ports. Access your applications at:

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- PostgreSQL: localhost:5432
- pgAdmin: http://localhost:5050

## File System Performance Tips

1. **Use WSL file system**: Work in `/home/user/` not `/mnt/c/`
2. **Avoid cross-filesystem operations**: Don't edit WSL files from Windows apps
3. **Use VS Code Remote-WSL**: Best integration and performance
4. **Enable Windows Defender exclusions**: Add WSL directories to exclusions

## Troubleshooting Quick Fixes

```bash
# Restart WSL
wsl.exe --shutdown
wsl.exe

# Check WSL version
wsl.exe --list --verbose

# Update WSL
wsl.exe --update

# Reset networking
wsl.exe --shutdown
# Restart Windows Terminal
```

## Next Steps

1. Configure VS Code Remote-WSL (see `VSCODE_WSL_SETUP.md`)
2. Set up debugging environment
3. Review WSL troubleshooting guide
4. Optimize your daily workflow

This setup provides optimal performance for Kairos BCP development in WSL, eliminating the complexity of dual Windows/WSL environments.