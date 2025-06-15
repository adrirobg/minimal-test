#!/bin/bash
# WSL Status Check Script - Comprehensive development environment status

echo "🔍 WSL Development Environment Status"
echo "===================================="

# WSL Environment Info
echo ""
echo "📊 WSL Environment:"
echo "   Distribution: $(cat /etc/os-release | grep PRETTY_NAME | cut -d'"' -f2)"
echo "   Kernel: $(uname -r)"
echo "   Architecture: $(uname -m)"

# Check if running in optimal location
CURRENT_DIR=$(pwd)
echo "   Current directory: $CURRENT_DIR"
if [[ $CURRENT_DIR == /mnt/c/* ]]; then
    echo "   ⚠️  WARNING: Running from Windows file system (slow)"
    echo "   💡 Consider moving to: ~/projects/kairos-bcp"
elif [[ $CURRENT_DIR == /home/* ]]; then
    echo "   ✅ Running from WSL native file system (optimal)"
fi

# System Resources
echo ""
echo "💾 System Resources:"
echo "   Memory: $(free -h | grep Mem | awk '{print $3 "/" $2 " (" int($3/$2*100) "%)"}')"
echo "   Disk: $(df -h /home | awk 'NR==2 {print $3 "/" $2 " (" $5 ")"}')"
echo "   CPU Load: $(uptime | awk -F'load average:' '{print $2}')"

# Check essential tools
echo ""
echo "🛠️  Development Tools:"

check_tool() {
    local tool=$1
    local name=$2
    if command -v "$tool" &> /dev/null; then
        local version=$($tool --version 2>/dev/null | head -n1 | cut -d' ' -f1-3 || echo "installed")
        echo "   ✅ $name: $version"
        return 0
    else
        echo "   ❌ $name: not found"
        return 1
    fi
}

check_tool "git" "Git"
check_tool "docker" "Docker"
check_tool "docker-compose" "Docker Compose"
check_tool "node" "Node.js"
check_tool "npm" "npm"
check_tool "python3" "Python"
check_tool "poetry" "Poetry"
check_tool "code" "VS Code"

# Docker Service Status
echo ""
echo "🐳 Docker Status:"
if sudo service docker status > /dev/null 2>&1; then
    echo "   ✅ Docker service is running"
    
    # Docker system info
    DOCKER_VERSION=$(docker --version 2>/dev/null | cut -d' ' -f3 | sed 's/,//')
    echo "   📦 Docker version: $DOCKER_VERSION"
    
    # Check if user can access Docker without sudo
    if docker ps > /dev/null 2>&1; then
        echo "   ✅ Docker access: OK (no sudo required)"
    else
        echo "   ⚠️  Docker access: requires sudo (check docker group membership)"
    fi
    
    # Docker disk usage
    DOCKER_SIZE=$(docker system df --format "table {{.Size}}" 2>/dev/null | tail -n +2 | head -n1 || echo "Unknown")
    echo "   💾 Docker disk usage: $DOCKER_SIZE"
    
else
    echo "   ❌ Docker service is not running"
    echo "   💡 Start with: sudo service docker start"
fi

# Project Services Status
echo ""
echo "🚀 Project Services:"

if [ -f "docker-compose.yml" ]; then
    echo "   📄 docker-compose.yml: found"
    
    # Check if services are running
    if docker-compose ps > /dev/null 2>&1; then
        RUNNING_SERVICES=$(docker-compose ps --services --filter status=running 2>/dev/null | wc -l)
        TOTAL_SERVICES=$(docker-compose ps --services 2>/dev/null | wc -l)
        echo "   🏃 Running services: $RUNNING_SERVICES/$TOTAL_SERVICES"
        
        # List service status
        if [ "$TOTAL_SERVICES" -gt 0 ]; then
            echo ""
            echo "   Service Details:"
            docker-compose ps --format "table {{.Name}}\t{{.State}}\t{{.Ports}}" 2>/dev/null | while IFS= read -r line; do
                echo "     $line"
            done
        fi
    else
        echo "   ❌ Unable to check service status"
    fi
else
    echo "   ❌ docker-compose.yml: not found"
    echo "   💡 Are you in the project root directory?"
fi

# Network Connectivity
echo ""
echo "🌐 Network Connectivity:"

check_url() {
    local url=$1
    local name=$2
    if curl -s --connect-timeout 3 "$url" > /dev/null 2>&1; then
        echo "   ✅ $name: accessible"
        return 0
    else
        echo "   ❌ $name: not accessible"
        return 1
    fi
}

check_url "http://localhost:3000" "Frontend (3000)"
check_url "http://localhost:8000/health" "Backend API (8000)"
check_url "http://localhost:5432" "PostgreSQL (5432)"
check_url "http://localhost:5050" "pgAdmin (5050)"

# VS Code Integration
echo ""
echo "🖥️  VS Code Integration:"
if [ -d ".vscode" ]; then
    echo "   ✅ .vscode directory: found"
    
    if [ -f ".vscode/settings.json" ]; then
        echo "   ✅ VS Code settings: configured"
    else
        echo "   ⚠️  VS Code settings: not found"
    fi
    
    if [ -f ".vscode/launch.json" ]; then
        echo "   ✅ Debug configuration: configured"
    else
        echo "   ⚠️  Debug configuration: not found"
    fi
    
    if [ -f ".vscode/extensions.json" ]; then
        echo "   ✅ Recommended extensions: configured"
    else
        echo "   ⚠️  Recommended extensions: not found"
    fi
else
    echo "   ❌ .vscode directory: not found"
    echo "   💡 Run 'code .' to create VS Code workspace"
fi

# Performance Indicators
echo ""
echo "⚡ Performance Indicators:"

# File operation speed test
START_TIME=$(date +%s.%N)
find . -name "*.py" -o -name "*.ts" -o -name "*.tsx" | head -100 > /dev/null 2>&1
END_TIME=$(date +%s.%N)
FIND_TIME=$(echo "$END_TIME - $START_TIME" | bc -l 2>/dev/null || echo "0.1")
echo "   🔍 File search speed: ${FIND_TIME}s (lower is better)"

# Docker response time
if docker ps > /dev/null 2>&1; then
    START_TIME=$(date +%s.%N)
    docker ps > /dev/null 2>&1
    END_TIME=$(date +%s.%N)
    DOCKER_TIME=$(echo "$END_TIME - $START_TIME" | bc -l 2>/dev/null || echo "0.1")
    echo "   🐳 Docker response: ${DOCKER_TIME}s"
fi

# Recommendations
echo ""
echo "💡 Recommendations:"

# Check common issues
RECOMMENDATIONS=()

if [[ $CURRENT_DIR == /mnt/c/* ]]; then
    RECOMMENDATIONS+=("Move project to WSL native file system for 10x better performance")
fi

if ! docker ps > /dev/null 2>&1 && command -v docker &> /dev/null; then
    RECOMMENDATIONS+=("Add user to docker group: sudo usermod -aG docker \$USER")
fi

if ! command -v code &> /dev/null; then
    RECOMMENDATIONS+=("Install VS Code Remote-WSL extension for better development experience")
fi

if [ ! -f ".vscode/settings.json" ]; then
    RECOMMENDATIONS+=("Configure VS Code workspace settings for optimal development")
fi

# Check memory usage
MEM_USAGE=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')
if [ "$MEM_USAGE" -gt 80 ]; then
    RECOMMENDATIONS+=("High memory usage detected ($MEM_USAGE%) - consider increasing WSL memory limit")
fi

# Check inotify limits
INOTIFY_LIMIT=$(cat /proc/sys/fs/inotify/max_user_watches)
if [ "$INOTIFY_LIMIT" -lt 524288 ]; then
    RECOMMENDATIONS+=("Increase inotify limits for better file watching performance")
fi

if [ ${#RECOMMENDATIONS[@]} -eq 0 ]; then
    echo "   🎉 Everything looks good! No recommendations at this time."
else
    for i in "${!RECOMMENDATIONS[@]}"; do
        echo "   $((i+1)). ${RECOMMENDATIONS[$i]}"
    done
fi

echo ""
echo "📚 More Information:"
echo "   WSL Setup Guide: ./WSL_QUICK_START.md"
echo "   Performance Tips: ./WSL_PERFORMANCE_TIPS.md"
echo "   Troubleshooting: ./WSL_TROUBLESHOOTING.md"