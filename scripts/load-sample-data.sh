#!/bin/bash
# Load Sample Data Script - Add test data to existing database

set -e

echo "📝 Kairos BCP - Load Sample Data"
echo "================================"

# Check if database is running
if ! docker-compose ps postgres | grep -q "Up"; then
    echo "❌ PostgreSQL container is not running!"
    echo "   Start it with: docker-compose up -d postgres"
    exit 1
fi

# Check if backend is running
if ! docker-compose ps backend | grep -q "Up"; then
    echo "❌ Backend container is not running!"
    echo "   Start it with: docker-compose up -d backend"
    exit 1
fi

echo "🔧 Loading sample data..."

# Wait for database to be ready
echo "   ⏳ Waiting for database..."
timeout 30s bash -c 'until docker-compose exec postgres pg_isready -U kairos_user -d kairos_bcp_dev &>/dev/null; do sleep 2; done'

# Run sample data script
echo "   📋 Creating sample users, projects, and notes..."
if docker-compose exec backend python sample_data.py; then
    echo ""
    echo "✅ Sample data loaded successfully!"
    echo ""
    echo "🎯 Test accounts available:"
    echo "   Test User:"
    echo "     Email: test@example.com"
    echo "     Password: test123"
    echo ""
    echo "   Developer User:"
    echo "     Email: dev@kairos.local"
    echo "     Password: developer123"
    echo ""
    echo "📊 Sample data includes:"
    echo "   • 2 users with different roles"
    echo "   • 3 projects with various themes"
    echo "   • Multiple notes with sample content"
    echo "   • Keywords for categorization"
    echo "   • External sources for reference"
    echo ""
    echo "🔧 Test the data:"
    echo "   • Login at: http://localhost:3000"
    echo "   • API docs: http://localhost:8000/docs"
    echo "   • Database: http://localhost:8080"
else
    echo ""
    echo "❌ Failed to load sample data!"
    echo "   Check backend logs: docker-compose logs backend"
    echo "   Try database reset: ./scripts/reset-db.sh"
    exit 1
fi