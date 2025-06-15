#!/bin/bash
# WSL-Optimized Database Reset Script - Fresh start with clean database

set -e

echo "💾 Kairos BCP - WSL Database Reset"
echo "=================================="

# WSL Environment Check
if ! grep -q microsoft /proc/version; then
    echo "⚠️  This script is optimized for WSL environments"
fi

# Ensure Docker is running
if ! docker ps &> /dev/null; then
    echo "🔧 Starting Docker service..."
    sudo service docker start
    sleep 2
fi

# Warning
echo "⚠️  WARNING: This will delete ALL data in the database!"
echo "   - All users, projects, notes will be lost"
echo "   - Fresh sample data will be created"
echo ""
read -p "Are you sure you want to continue? (y/N): " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Database reset cancelled"
    exit 0
fi

echo ""
echo "🔧 Resetting database..."

# Stop database container
echo "   📦 Stopping PostgreSQL container..."
docker-compose stop postgres

# Remove database volume
echo "   🗑️  Removing database volume..."
docker volume rm kairos-bcp_postgres_data 2>/dev/null || true

# Start database container
echo "   🚀 Starting PostgreSQL container..."
docker-compose up -d postgres

# Wait for PostgreSQL to be ready
echo "   ⏳ Waiting for PostgreSQL to start..."
timeout 60s bash -c 'until docker-compose exec postgres pg_isready -U kairos_user -d kairos_bcp_dev &>/dev/null; do sleep 2; done'

# Run database initialization
echo "   📋 Initializing database schema..."
docker-compose exec backend python init_db.py

# Create sample data
echo "   📝 Creating sample data..."
docker-compose exec backend python sample_data.py

echo ""
echo "✅ Database reset complete!"
echo ""
echo "🎯 Test accounts created:"
echo "   Test User:"
echo "     Email: test@example.com"
echo "     Password: test123"
echo ""
echo "   Developer User:"
echo "     Email: dev@kairos.local"
echo "     Password: developer123"
echo ""
echo "📊 Access database:"
echo "   pgAdmin: http://localhost:8080"
echo "   Login: admin@kairos.dev / admin"
echo ""
echo "🔧 Backend API: http://localhost:8000/docs"
echo ""
echo "💡 WSL Tips:"
echo "   Open browser: ./scripts/open-browser.sh"
echo "   Check status: ./scripts/wsl-status.sh"
echo "   Open VS Code: code ."