# WSL Performance Debugging Guide

Advanced performance analysis and optimization for WSL development with Kairos BCP.

## 🔍 Performance Monitoring

### System Resource Monitoring
```bash
# Monitor real-time system performance
htop  # Interactive process viewer

# Monitor I/O operations
iotop  # Requires: sudo apt install iotop

# Monitor disk usage
df -h  # Disk space
du -sh ~/projects/kairos-bcp/  # Project size

# Monitor memory usage
free -h  # Memory usage
cat /proc/meminfo  # Detailed memory info

# Monitor WSL from Windows (PowerShell)
Get-Process vmmem  # WSL memory usage from Windows
```

### File System Performance
```bash
# Test file system performance
# Write test
time dd if=/dev/zero of=test_file bs=1M count=1000
# Read test
time dd if=test_file of=/dev/null bs=1M
# Clean up
rm test_file

# Test random I/O performance
sudo apt install fio
fio --name=random-read --ioengine=posix --rw=randread --bs=4k --numjobs=1 --size=1g --iodepth=1 --runtime=60 --time_based --group_reporting
```

### Network Performance
```bash
# Test network latency
ping -c 10 google.com

# Test network throughput
curl -w "@curl-format.txt" -o /dev/null -s "https://httpbin.org/get"

# Create curl-format.txt for detailed timing
cat > curl-format.txt << 'EOF'
     time_namelookup:  %{time_namelookup}\n
        time_connect:  %{time_connect}\n
     time_appconnect:  %{time_appconnect}\n
    time_pretransfer:  %{time_pretransfer}\n
       time_redirect:  %{time_redirect}\n
  time_starttransfer:  %{time_starttransfer}\n
                     ----------\n
          time_total:  %{time_total}\n
EOF
```

## 🚀 Development Server Performance

### Node.js Performance Analysis
```bash
cd ~/projects/kairos-bcp/frontend/

# Profile Next.js build performance
ANALYZE=true npm run build

# Monitor Node.js memory usage
node --inspect --max-old-space-size=4096 node_modules/.bin/next dev

# Profile runtime performance
npm install -g clinic
clinic doctor -- npm run dev
```

### Python Performance Analysis
```bash
cd ~/projects/kairos-bcp/backend/

# Profile Python application startup
time poetry run uvicorn app.main:app --reload

# Memory profiling with memory_profiler
poetry add memory-profiler
poetry run python -m memory_profiler app/main.py

# CPU profiling with py-spy
pip install py-spy
py-spy record -o profile.svg -- poetry run uvicorn app.main:app

# Line-by-line profiling
poetry add line_profiler
# Add @profile decorator to functions, then:
poetry run kernprof -l -v app/main.py
```

### Database Performance Analysis
```bash
# PostgreSQL performance monitoring
docker-compose exec postgres psql -U postgres -d kairos_bcp -c "
SELECT query, calls, total_time, mean_time 
FROM pg_stat_statements 
ORDER BY total_time DESC 
LIMIT 10;"

# Enable query logging in PostgreSQL
docker-compose exec postgres psql -U postgres -c "
ALTER SYSTEM SET log_statement = 'all';
ALTER SYSTEM SET log_min_duration_statement = 100;
SELECT pg_reload_conf();"

# Monitor slow queries
docker-compose logs postgres | grep "duration:"
```

## 📊 Performance Benchmarking

### Comparative Benchmarks
```bash
# Compare WSL vs Windows performance

# File operations benchmark
time find ~/projects/kairos-bcp/ -name "*.py" | wc -l  # WSL
time find /mnt/c/Users/YourName/Projects/kairos-bcp/ -name "*.py" | wc -l  # Windows

# Build performance comparison
cd ~/projects/kairos-bcp/frontend/
time npm install  # WSL
cd /mnt/c/Users/YourName/Projects/kairos-bcp/frontend/
time npm install  # Windows (if applicable)

# Docker performance
time docker build -t test-image .  # WSL Docker
```

### Application-Specific Benchmarks
```bash
# API endpoint performance
ab -n 1000 -c 10 http://localhost:8000/health  # Apache Bench
# Or use wrk:
wrk -t12 -c400 -d30s http://localhost:8000/health

# Database query performance
docker-compose exec postgres psql -U postgres -d kairos_bcp -c "
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM notes WHERE project_id = 1;"

# Frontend bundle analysis
cd frontend/
npm run build
npm run analyze  # If configured
```

## 🔧 Performance Optimization

### WSL Configuration Tuning
```bash
# Optimize WSL memory configuration
# Create/edit C:\Users\%USERNAME%\.wslconfig:
[wsl2]
memory=8GB           # Adjust based on your system
processors=4         # Half of your CPU cores
swap=2GB            # Enable swap for memory overflow
localhostForwarding=true

# Restart WSL to apply
wsl.exe --shutdown
```

### File System Optimization
```bash
# Increase inotify limits for file watching
echo 'fs.inotify.max_user_watches=1048576' | sudo tee -a /etc/sysctl.conf
echo 'fs.inotify.max_user_instances=1024' | sudo tee -a /etc/sysctl.conf
echo 'fs.inotify.max_queued_events=32768' | sudo tee -a /etc/sysctl.conf
sudo sysctl -p

# Optimize file system performance
# Add to /etc/fstab (if needed):
tmpfs /tmp tmpfs defaults,noatime,mode=1777 0 0
```

### Docker Performance Tuning
```bash
# Optimize Docker daemon configuration
sudo tee /etc/docker/daemon.json > /dev/null << 'EOF'
{
  "storage-driver": "overlay2",
  "log-driver": "local",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "default-ulimits": {
    "nofile": {
      "Name": "nofile",
      "Hard": 64000,
      "Soft": 64000
    }
  }
}
EOF

sudo service docker restart
```

### Application-Level Optimization
```bash
# Node.js optimization
export NODE_OPTIONS="--max-old-space-size=4096"
export UV_THREADPOOL_SIZE=4

# Python optimization
export PYTHONUNBUFFERED=1
export PYTHONOPTIMIZE=1

# Add to ~/.bashrc for persistence
echo 'export NODE_OPTIONS="--max-old-space-size=4096"' >> ~/.bashrc
echo 'export PYTHONUNBUFFERED=1' >> ~/.bashrc
```

## 🐛 Performance Issue Diagnosis

### Common Performance Bottlenecks
```bash
# 1. File system location check
pwd  # Should be /home/user/..., not /mnt/c/...

# 2. Memory pressure check
free -h
# If swap usage is high, increase WSL memory

# 3. CPU usage check
top -o %CPU
# Look for high CPU processes

# 4. Disk I/O check
iotop -ao
# Look for high I/O processes

# 5. Network latency check
ping -c 5 localhost
# Should be < 1ms
```

### Performance Regression Analysis
```bash
# Create performance baseline
cat > performance-baseline.sh << 'EOF'
#!/bin/bash
echo "=== Performance Baseline Test ==="
echo "Date: $(date)"
echo "WSL Version: $(wsl.exe --version)"
echo "System Info: $(uname -a)"

echo -e "\n=== File System Performance ==="
time find ~/projects/kairos-bcp/ -name "*.py" | wc -l

echo -e "\n=== Build Performance ==="
cd ~/projects/kairos-bcp/frontend/
time npm install --force

echo -e "\n=== Docker Performance ==="
time docker-compose up -d

echo -e "\n=== API Response Time ==="
curl -w "Total time: %{time_total}s\n" -o /dev/null -s http://localhost:8000/health

echo -e "\n=== Database Query Performance ==="
docker-compose exec postgres psql -U postgres -d kairos_bcp -c "
\timing on
SELECT COUNT(*) FROM notes;
"
EOF

chmod +x performance-baseline.sh
./performance-baseline.sh | tee performance-$(date +%Y%m%d-%H%M%S).log
```

### Memory Leak Detection
```bash
# Monitor memory usage over time
watch -n 5 'free -h && docker stats --no-stream'

# Python memory profiling
poetry add pympler
# Add to your code:
from pympler import tracker
tr = tracker.SummaryTracker()
# ... your code ...
tr.print_diff()

# Node.js memory profiling
npm install -g memwatch-next
# Add to your code:
const memwatch = require('memwatch-next');
memwatch.on('leak', (info) => {
  console.log('Memory leak detected:', info);
});
```

## 📈 Performance Monitoring Dashboard

### Real-time Monitoring Setup
```bash
# Install monitoring tools
sudo apt install htop iotop netstat-nat

# Create monitoring script
cat > monitor-performance.sh << 'EOF'
#!/bin/bash
while true; do
    clear
    echo "=== WSL Performance Monitor ==="
    echo "Time: $(date)"
    echo
    
    echo "=== Memory Usage ==="
    free -h
    echo
    
    echo "=== CPU Usage ==="
    uptime
    echo
    
    echo "=== Disk Usage ==="
    df -h | grep -E "(Filesystem|/home|/tmp)"
    echo
    
    echo "=== Docker Stats ==="
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
    echo
    
    echo "=== Network Connections ==="
    netstat -tuln | grep -E "(3000|8000|5432|5050)"
    
    sleep 5
done
EOF

chmod +x monitor-performance.sh
```

### Performance Alerting
```bash
# Create performance alert script
cat > performance-alerts.sh << 'EOF'
#!/bin/bash

# Thresholds
MEM_THRESHOLD=80
CPU_THRESHOLD=80
DISK_THRESHOLD=90

# Check memory usage
MEM_USAGE=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')
if [ $MEM_USAGE -gt $MEM_THRESHOLD ]; then
    echo "WARNING: Memory usage is ${MEM_USAGE}%"
fi

# Check disk usage
DISK_USAGE=$(df -h /home | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt $DISK_THRESHOLD ]; then
    echo "WARNING: Disk usage is ${DISK_USAGE}%"
fi

# Check Docker container health
docker-compose ps | grep -v "Up" | grep -v "Name" && echo "WARNING: Some containers are not running"
EOF

chmod +x performance-alerts.sh

# Run alerts periodically
(crontab -l ; echo "*/5 * * * * ~/performance-alerts.sh") | crontab -
```

## 🔍 Advanced Profiling

### System Call Tracing
```bash
# Trace system calls for performance analysis
sudo apt install strace

# Trace application startup
strace -c -f poetry run uvicorn app.main:app --reload

# Trace specific operations
strace -e trace=file npm run dev
```

### Network Traffic Analysis
```bash
# Monitor network traffic
sudo apt install tcpdump wireshark-common

# Capture HTTP traffic
sudo tcpdump -i any -A -s 0 'port 8000'

# Analyze container network traffic
docker run --rm --net container:$(docker-compose ps -q backend) nicolaka/netshoot tcpdump -i eth0
```

### Application Performance Metrics
```bash
# Create custom metrics collection
cat > collect-metrics.sh << 'EOF'
#!/bin/bash
LOG_FILE="performance-metrics-$(date +%Y%m%d).log"

while true; do
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
    
    # System metrics
    MEM_USAGE=$(free | grep Mem | awk '{printf "%.1f", $3/$2 * 100.0}')
    CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | sed 's/%us,//')
    DISK_USAGE=$(df -h /home | awk 'NR==2 {print $5}' | sed 's/%//')
    
    # Application metrics
    API_RESPONSE=$(curl -w "%{time_total}" -o /dev/null -s http://localhost:8000/health 2>/dev/null || echo "N/A")
    FRONTEND_STATUS=$(curl -o /dev/null -s -w "%{http_code}" http://localhost:3000 2>/dev/null || echo "N/A")
    
    # Docker metrics
    CONTAINER_COUNT=$(docker ps | wc -l)
    
    echo "$TIMESTAMP,MEM:$MEM_USAGE,CPU:$CPU_USAGE,DISK:$DISK_USAGE,API:$API_RESPONSE,FE:$FRONTEND_STATUS,CONTAINERS:$CONTAINER_COUNT" >> $LOG_FILE
    
    sleep 60
done
EOF

chmod +x collect-metrics.sh
# Run in background: nohup ./collect-metrics.sh &
```

This comprehensive performance debugging guide helps identify and resolve performance issues in WSL-based Kairos BCP development environments.