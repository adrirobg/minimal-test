# WSL Performance Tips for Kairos BCP Development

Advanced performance optimization techniques for WSL development with Kairos BCP.

## File System Performance

### 1. File System Choice

**Performance Ranking** (fastest to slowest):
1. WSL native (`/home/user/`) - **Use this**
2. WSL mounted (`/mnt/wsl/`) - **Avoid**  
3. Windows mounted (`/mnt/c/`) - **Never use for development**

```bash
# ✅ FAST: WSL native file system
~/projects/kairos-bcp/

# 🐌 SLOW: Windows file system mounted in WSL
/mnt/c/Users/Username/Projects/kairos-bcp/
```

### 2. File Operations Optimization

```bash
# Use rsync for large file operations
rsync -av --progress /mnt/c/source/ ~/destination/

# Use find with -type for faster searches
find . -type f -name "*.py" | head -10

# Use ripgrep (rg) instead of grep
rg "function" --type py
```

## Memory and CPU Optimization

### 1. WSL Configuration

Create optimal `.wslconfig` in `C:\Users\%USERNAME%\.wslconfig`:

```ini
[wsl2]
# Memory allocation (adjust based on your system)
memory=8GB
# CPU cores (use half of your total cores)
processors=4
# Swap size
swap=2GB
# Swap file location (optional)
swapfile=C:\\temp\\wsl-swap.vhdx

# Network settings
localhostForwarding=true
firewall=false

# Performance settings
nestedVirtualization=true
debugConsole=false
```

### 2. Systemd Optimization

Enable systemd in WSL for better service management:

```bash
# Add to /etc/wsl.conf
sudo tee /etc/wsl.conf > /dev/null <<EOF
[boot]
systemd=true

[automount]
enabled=true
options="metadata,uid=1000,gid=1000,umask=22"
mountFsTab=false

[network]
generateHosts=true
generateResolvConf=true

[interop]
enabled=true
appendWindowsPath=true
EOF
```

## Development Server Optimization

### 1. Node.js Performance

```bash
# Increase Node.js memory limit
export NODE_OPTIONS="--max-old-space-size=4096"

# Use faster package manager
npm install -g pnpm
# or
npm install -g yarn

# Enable corepack for package manager optimization
corepack enable
```

### 2. Python Performance

```bash
# Use UV for faster Python package management
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.cargo/bin:$PATH"

# Alternative to Poetry for faster installs
uv pip install -r requirements.txt
```

### 3. Docker Optimization

```bash
# Enable Docker BuildKit
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

# Use multi-stage builds
# Use .dockerignore to exclude unnecessary files
# Mount cache volumes for dependencies
```

## File Watching and Hot Reload

### 1. Increase inotify Limits

```bash
# Check current limits
cat /proc/sys/fs/inotify/max_user_watches

# Increase limits permanently
echo 'fs.inotify.max_user_watches=1048576' | sudo tee -a /etc/sysctl.conf
echo 'fs.inotify.max_user_instances=1024' | sudo tee -a /etc/sysctl.conf
echo 'fs.inotify.max_queued_events=32768' | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

### 2. File Watching Configuration

```bash
# For Next.js development
# In frontend/next.config.ts
const nextConfig = {
  experimental: {
    fsChecker: false, // Disable FS checker for better performance
  },
  webpack: (config) => {
    config.watchOptions = {
      poll: 1000,
      aggregateTimeout: 300,
    }
    return config
  }
}
```

## Network Performance

### 1. Localhost Forwarding

```bash
# Add to ~/.bashrc for better networking
export WSL_HOST=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}')
export DISPLAY=$WSL_HOST:0.0

# Test network performance
curl -w "@curl-format.txt" -o /dev/null -s "http://localhost:3000"
```

### 2. DNS Optimization

```bash
# Use faster DNS servers
sudo tee /etc/systemd/resolved.conf > /dev/null <<EOF
[Resolve]
DNS=1.1.1.1 8.8.8.8
Domains=~
FallbackDNS=1.0.0.1 8.8.4.4
DNSSEC=no
DNSOverTLS=no
Cache=yes
DNSStubListener=yes
EOF

sudo systemctl restart systemd-resolved
```

## Database Performance

### 1. PostgreSQL in Docker

```yaml
# Optimized PostgreSQL configuration in docker-compose.yml
postgres:
  image: postgres:15-alpine
  shm_size: 256mb
  command: |
    postgres
    -c shared_preload_libraries=pg_stat_statements
    -c max_connections=200
    -c shared_buffers=256MB
    -c effective_cache_size=1GB
    -c maintenance_work_mem=64MB
    -c checkpoint_completion_target=0.9
    -c wal_buffers=16MB
    -c default_statistics_target=100
```

### 2. pgAdmin Performance

```bash
# Reduce pgAdmin resource usage
export PGADMIN_CONFIG_WTF_CSRF_TIME_LIMIT=None
export PGADMIN_CONFIG_SESSION_COOKIE_SAMESITE='Lax'
export PGADMIN_CONFIG_SESSION_COOKIE_SECURE=False
```

## Development Tools Performance

### 1. Git Performance

```bash
# Enable Git performance features
git config --global core.preloadindex true
git config --global core.fscache true
git config --global gc.auto 256
git config --global feature.manyFiles true
```

### 2. Shell Performance

```bash
# Use zsh with powerlevel10k for better performance
sudo apt install zsh
sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"

# Or use fish shell
sudo apt install fish
```

## Monitoring and Profiling

### 1. Resource Monitoring

```bash
# Monitor WSL resource usage
# In PowerShell
Get-Process vmmem

# In WSL
htop
iotop
```

### 2. Performance Profiling

```bash
# Profile application startup
time npm run dev
time poetry run python main.py

# Monitor file system operations
sudo apt install inotify-tools
inotifywatch -r ~/projects/kairos-bcp/
```

## Windows Defender Optimization

**CRITICAL**: Add WSL directories to Windows Defender exclusions:

1. Open Windows Security
2. Go to Virus & threat protection
3. Add exclusions for:
   - `%USERPROFILE%\AppData\Local\Docker`
   - WSL distribution location (usually `C:\Users\%USERNAME%\AppData\Local\Packages\CanonicalGroupLimited*`)
   - Your WSL home directory accessible via `\\wsl$\Ubuntu\home\username`

## Performance Benchmarking

```bash
# File system benchmark
time dd if=/dev/zero of=testfile bs=1M count=1000
rm testfile

# Network benchmark
curl -w "@curl-format.txt" -o /dev/null -s "http://localhost:3000"

# Database benchmark
time psql -h localhost -U postgres -c "SELECT COUNT(*) FROM notes;"
```

## Quick Performance Checklist

- [ ] Project located in WSL native file system (`~/projects/`)
- [ ] `.wslconfig` optimized for your system
- [ ] Windows Defender exclusions configured
- [ ] inotify limits increased
- [ ] Docker using WSL 2 backend
- [ ] VS Code Remote-WSL extension installed
- [ ] Node.js memory limits increased
- [ ] Git performance features enabled
- [ ] systemd enabled in WSL

Following these tips will provide optimal performance for Kairos BCP development in WSL.