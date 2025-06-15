# WSL Docker Issues and Solutions

Specific troubleshooting guide for Docker integration with WSL in Kairos BCP development.

## 🐳 Docker Installation Issues

### Docker Not Found in WSL
```bash
# Check if Docker is installed
docker --version

# If not installed, install Docker in WSL (not Docker Desktop)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Start Docker service
sudo service docker start

# Enable auto-start
sudo systemctl enable docker
```

### Docker Desktop Conflicts
```bash
# If you have Docker Desktop installed, it may conflict with WSL Docker

# Option 1: Use Docker Desktop with WSL 2 backend
# - Enable "Use the WSL 2 based engine" in Docker Desktop settings
# - Enable WSL integration for your Ubuntu distribution

# Option 2: Uninstall Docker Desktop and use native WSL Docker (recommended)
# - Uninstall Docker Desktop from Windows
# - Install Docker directly in WSL (see above)
```

### Permission Denied Errors
```bash
# Common Docker permission error:
# "permission denied while trying to connect to the Docker daemon socket"

# Solution 1: Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Solution 2: Start Docker service
sudo service docker start

# Solution 3: Fix socket permissions
sudo chmod 666 /var/run/docker.sock

# Test Docker access
docker run hello-world
```

## 🔄 Docker Service Issues

### Docker Daemon Not Running
```bash
# Check Docker service status
sudo service docker status

# Start Docker service
sudo service docker start

# If service fails to start, check logs
sudo journalctl -u docker.service

# Common fix: restart with clean state
sudo systemctl daemon-reload
sudo service docker restart
```

### Docker Daemon Socket Issues
```bash
# Error: "Cannot connect to the Docker daemon at unix:///var/run/docker.sock"

# Check if socket exists
ls -la /var/run/docker.sock

# If missing, restart Docker
sudo service docker restart

# If permissions issue
sudo chmod 666 /var/run/docker.sock

# For permanent fix, ensure user is in docker group
groups $USER | grep docker
```

### Auto-start Docker on WSL Boot
```bash
# Add to ~/.bashrc for automatic startup
echo '# Start Docker service automatically' >> ~/.bashrc
echo 'if ! sudo service docker status > /dev/null 2>&1; then' >> ~/.bashrc
echo '    sudo service docker start > /dev/null 2>&1' >> ~/.bashrc
echo 'fi' >> ~/.bashrc

# Reload bashrc
source ~/.bashrc

# Alternative: Use systemd (if enabled in WSL)
sudo systemctl enable docker
```

## 🏗️ Docker Compose Issues

### Docker Compose Not Found
```bash
# Check if docker-compose is installed
docker-compose --version

# If not found, install it
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker-compose --version

# Alternative: Install via pip
pip3 install docker-compose
```

### Docker Compose File Issues
```bash
# Common issues with docker-compose.yml in WSL

# Issue 1: Windows line endings
# Convert CRLF to LF
dos2unix docker-compose.yml

# Issue 2: File permissions
chmod 644 docker-compose.yml

# Issue 3: Indentation errors
# Use a YAML validator or VS Code YAML extension

# Test docker-compose file
docker-compose config
```

### Volume Mount Issues
```bash
# Issue: Windows paths don't work in WSL docker-compose.yml

# ❌ Wrong: Windows path
volumes:
  - C:\Users\Name\project:/app

# ✅ Correct: WSL path
volumes:
  - ./:/app
  - ~/projects/kairos-bcp:/app

# Check current volume mounts
docker-compose ps
docker inspect <container_name> | grep -A 10 "Mounts"
```

## 🗄️ Database Container Issues

### PostgreSQL Container Won't Start
```bash
# Check PostgreSQL container logs
docker-compose logs postgres

# Common issues and solutions:

# Issue 1: Port already in use
sudo lsof -i :5432
# Kill conflicting process or change port in docker-compose.yml

# Issue 2: Data directory permissions
docker-compose down
docker volume rm kairos_postgres_data
docker-compose up -d postgres

# Issue 3: Insufficient memory
# Add to docker-compose.yml:
services:
  postgres:
    mem_limit: 512m
    shm_size: 256mb
```

### Database Connection Refused
```bash
# Check if PostgreSQL is ready
docker-compose exec postgres pg_isready -U postgres

# Check container networking
docker-compose exec backend ping postgres
docker-compose exec postgres ping backend

# Verify database credentials in environment variables
docker-compose exec backend env | grep DATABASE

# Test connection manually
docker-compose exec postgres psql -U postgres -h localhost -p 5432
```

### pgAdmin Access Issues
```bash
# pgAdmin container not accessible at localhost:5050

# Check pgAdmin container logs
docker-compose logs pgadmin

# Common fixes:
# 1. Clear browser cache and cookies
# 2. Try incognito/private browsing mode
# 3. Check if port 5050 is free
sudo lsof -i :5050

# Access pgAdmin directly in container
docker-compose exec pgadmin sh
```

## 🚀 Performance Issues

### Slow Container Builds
```bash
# Issue: Docker builds are slow in WSL

# Solution 1: Use .dockerignore to exclude unnecessary files
cat > .dockerignore << EOF
node_modules
.git
.pytest_cache
__pycache__
.venv
.next
*.log
EOF

# Solution 2: Enable BuildKit for faster builds
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1
docker-compose build

# Solution 3: Use multi-stage builds efficiently
# Optimize Dockerfile for layer caching
```

### High Memory Usage
```bash
# Check Docker memory usage
docker stats

# Limit container memory in docker-compose.yml
services:
  backend:
    mem_limit: 512m
  frontend:
    mem_limit: 256m
  postgres:
    mem_limit: 512m

# Restart containers with new limits
docker-compose down
docker-compose up -d
```

### Slow File Watching
```bash
# Issue: Hot reload is slow or not working

# Ensure project is in WSL file system (not /mnt/c/)
pwd  # Should show /home/user/projects/...

# Increase inotify limits
echo 'fs.inotify.max_user_watches=1048576' | sudo tee -a /etc/sysctl.conf
sudo sysctl -p

# For Node.js applications, enable polling in next.config.ts:
module.exports = {
  webpack: (config) => {
    config.watchOptions = {
      poll: 1000,
      aggregateTimeout: 300,
    }
    return config
  }
}
```

## 🌐 Network Configuration

### Container Communication Issues
```bash
# Containers can't communicate with each other

# Check Docker network
docker network ls
docker network inspect kairos_default

# Ensure containers are on same network
docker-compose ps

# Test connectivity between containers
docker-compose exec backend ping postgres
docker-compose exec frontend ping backend

# If using custom networks, verify configuration in docker-compose.yml
```

### Host Access Issues
```bash
# Can't access containers from Windows host

# Check port forwarding
netstat -tulpn | grep :3000
netstat -tulpn | grep :8000

# Ensure containers bind to 0.0.0.0, not 127.0.0.1
# In docker-compose.yml:
ports:
  - "3000:3000"  # ✅ Correct
  - "127.0.0.1:3000:3000"  # ❌ Wrong for WSL

# Manual port forwarding if needed (PowerShell as Admin):
netsh interface portproxy add v4tov4 listenport=3000 listenaddress=0.0.0.0 connectport=3000 connectaddress=172.17.0.1
```

### DNS Resolution Problems
```bash
# Containers can't resolve external domains

# Check DNS in container
docker-compose exec backend nslookup google.com

# Fix DNS configuration
# Add to docker-compose.yml:
services:
  backend:
    dns:
      - 8.8.8.8
      - 1.1.1.1

# Or fix host DNS
sudo tee /etc/systemd/resolved.conf > /dev/null <<EOF
[Resolve]
DNS=1.1.1.1 8.8.8.8
FallbackDNS=1.0.0.1 8.8.4.4
EOF
sudo systemctl restart systemd-resolved
```

## 💾 Storage and Volume Issues

### Volume Mount Failures
```bash
# Error: "no such file or directory" when mounting volumes

# Check source path exists
ls -la ~/projects/kairos-bcp/

# Use absolute paths for clarity
# In docker-compose.yml:
volumes:
  - /home/user/projects/kairos-bcp:/app  # Absolute path
  - ./:/app  # Relative path (must run from correct directory)

# Fix permissions on mounted directories
sudo chown -R $USER:$USER ~/projects/kairos-bcp/
```

### Persistent Data Issues
```bash
# Database data not persisting between container restarts

# Check named volumes
docker volume ls

# Inspect volume details
docker volume inspect kairos_postgres_data

# If data lost, check volume mount in docker-compose.yml:
services:
  postgres:
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:  # Named volume declaration
```

### Disk Space Issues
```bash
# Docker running out of space

# Check Docker disk usage
docker system df

# Clean up unused resources
docker system prune -a  # Warning: removes all unused images

# Clean up volumes (be careful!)
docker volume prune

# Check WSL disk usage
df -h

# If WSL disk full, clean up:
sudo apt autoremove
sudo apt autoclean
```

## 🔧 Docker Configuration Optimization

### WSL-Specific Docker Settings
```bash
# Create/edit daemon.json for optimal WSL performance
sudo mkdir -p /etc/docker
sudo tee /etc/docker/daemon.json > /dev/null << EOF
{
  "storage-driver": "overlay2",
  "log-driver": "local",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "dns": ["8.8.8.8", "1.1.1.1"],
  "default-address-pools": [
    {
      "base": "172.17.0.0/16",
      "size": 24
    }
  ]
}
EOF

# Restart Docker to apply changes
sudo service docker restart
```

### Memory and CPU Limits
```bash
# Optimize docker-compose.yml for WSL environment
services:
  backend:
    cpus: "0.5"
    mem_limit: 512m
    memswap_limit: 512m
    
  frontend:
    cpus: "0.5"
    mem_limit: 256m
    memswap_limit: 256m
    
  postgres:
    cpus: "0.5"
    mem_limit: 512m
    shm_size: 256mb
```

## 🔄 Emergency Recovery

### Complete Docker Reset
```bash
# Stop all containers
docker-compose down

# Remove all containers, networks, images
docker system prune -a --volumes

# Remove all Docker data (nuclear option)
sudo service docker stop
sudo rm -rf /var/lib/docker
sudo service docker start

# Rebuild everything
docker-compose up -d --build
```

### WSL Docker Service Reset
```bash
# Reset Docker installation in WSL
sudo apt remove docker-ce docker-ce-cli containerd.io
sudo rm -rf /var/lib/docker

# Reinstall Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Reconfigure user and restart
sudo usermod -aG docker $USER
newgrp docker
sudo service docker start
```

## 📋 Docker Health Checks

### Regular Diagnostics
```bash
# Run these commands regularly to check Docker health

# 1. Service status
sudo service docker status

# 2. Container status
docker-compose ps

# 3. Resource usage
docker stats --no-stream

# 4. System information
docker system info

# 5. Disk usage
docker system df

# 6. Network connectivity
docker-compose exec backend ping google.com
```

### Automated Health Script
```bash
# Create a health check script
cat > ~/check-docker-health.sh << 'EOF'
#!/bin/bash
echo "=== Docker Health Check ==="
echo "Docker service status:"
sudo service docker status | grep Active

echo -e "\nContainer status:"
docker-compose ps

echo -e "\nDocker disk usage:"
docker system df

echo -e "\nContainer resource usage:"
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"

echo -e "\nDocker version:"
docker --version
docker-compose --version
EOF

chmod +x ~/check-docker-health.sh

# Run health check
~/check-docker-health.sh
```

This guide addresses the most common Docker-specific issues in WSL environments for Kairos BCP development.