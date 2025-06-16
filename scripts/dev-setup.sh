#!/bin/bash
# WSL-Optimized Development Setup Script - Get coding in 2 minutes!

set -e

echo "🚀 Kairos BCP - WSL Development Setup"
echo "===================================="

# WSL Environment Check
echo "🔍 Checking WSL environment..."

# Check if running in WSL
if ! grep -q microsoft /proc/version; then
    echo "⚠️  This script is optimized for WSL. Consider using WSL for better performance."
fi

# Check file system location for optimal performance
CURRENT_DIR=$(pwd)
if [[ $CURRENT_DIR == /mnt/c/* ]]; then
    echo "⚠️  WARNING: You're running from Windows file system (/mnt/c/)"
    echo "   For optimal performance, move project to WSL file system:"
    echo "   cp -r $(pwd) ~/projects/kairos-bcp && cd ~/projects/kairos-bcp"
    echo ""
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 0
    fi
elif [[ $CURRENT_DIR == /home/* ]]; then
    echo "✅ Running from WSL native file system (optimal performance)"
fi

# Check prerequisites
echo "📋 Checking prerequisites..."

# Start Docker service if not running (WSL-specific)
if ! docker ps &> /dev/null; then
    echo "🔧 Starting Docker service..."
    sudo service docker start
    sleep 2
fi

if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker in WSL:"
    echo "   curl -fsSL https://get.docker.com -o get-docker.sh"
    echo "   sudo sh get-docker.sh"
    echo "   sudo usermod -aG docker \$USER"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose not found. Installing..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

echo "✅ Docker and Docker Compose found"

# Check if already running
if docker-compose ps | grep -q "Up"; then
    echo "⚠️  Development environment is already running!"
    echo "   Use 'docker-compose down' to stop it first."
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 0
    fi
fi

# Start development environment
echo ""
echo "🔧 Starting development environment..."
echo "   This may take a few minutes on first run..."

# Pull and build images
docker-compose pull
docker-compose build

# Start services
docker-compose up -d

# Wait for services to be ready
echo ""
echo "⏳ Waiting for services to start..."

# Wait for PostgreSQL
echo "   📦 Waiting for PostgreSQL..."
timeout 60s bash -c 'until docker-compose exec postgres pg_isready -U kairos_user -d kairos_bcp_dev &>/dev/null; do sleep 2; done'

# Wait for backend
echo "   🔧 Waiting for Backend API..."
timeout 60s bash -c 'until curl -s http://localhost:8000/health &>/dev/null; do sleep 2; done'

# Wait for frontend
echo "   📱 Waiting for Frontend..."
timeout 60s bash -c 'until curl -s -I http://localhost:3000 &>/dev/null; do sleep 2; done'

# Success message
echo ""
echo "🎉 Development environment is ready!"
echo ""
echo "📍 Access your application:"
echo "   Frontend:    http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Docs:    http://localhost:8000/docs"
echo "   Database:    http://localhost:8080 (admin@kairos.dev / admin)"
echo ""
echo "📝 Quick commands:"
echo "   View logs:   docker-compose logs -f"
echo "   Stop all:    docker-compose down"
echo "   Restart:     docker-compose restart"
echo ""
echo "🛠️  Happy coding! Edit files and they'll auto-reload."

# WSL-specific browser opening
read -p "Open browser windows in Windows? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Use Windows browser from WSL
    if command -v explorer.exe &> /dev/null; then
        echo "🌐 Opening applications in Windows browser..."
        explorer.exe "http://localhost:3000" &
        explorer.exe "http://localhost:8000/docs" &
        explorer.exe "http://localhost:8080" &
    elif command -v cmd.exe &> /dev/null; then
        cmd.exe /c start http://localhost:3000
        cmd.exe /c start http://localhost:8000/docs
        cmd.exe /c start http://localhost:8080
    fi
fi

echo ""
echo "💡 WSL Tips:"
echo "   Open VS Code: code ."
echo "   Check performance: ~/check-docker-health.sh"
echo "   WSL commands: wsl.exe --help"