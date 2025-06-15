#!/bin/bash
# WSL Browser Helper Script - Open development URLs in Windows browser

echo "🌐 Opening Kairos BCP development environment in browser..."

# Development URLs
FRONTEND_URL="http://localhost:3000"
BACKEND_URL="http://localhost:8000"
API_DOCS_URL="http://localhost:8000/docs"
PGADMIN_URL="http://localhost:5050"

# Check if services are running
echo "🔍 Checking if services are running..."

# Function to check if URL is accessible
check_url() {
    local url=$1
    local name=$2
    if curl -s --connect-timeout 3 "$url" > /dev/null 2>&1; then
        echo "✅ $name is running at $url"
        return 0
    else
        echo "❌ $name is not accessible at $url"
        return 1
    fi
}

# Check each service
FRONTEND_OK=false
BACKEND_OK=false
PGADMIN_OK=false

if check_url "$FRONTEND_URL" "Frontend"; then
    FRONTEND_OK=true
fi

if check_url "$BACKEND_URL/health" "Backend API"; then
    BACKEND_OK=true
fi

if check_url "$PGADMIN_URL" "pgAdmin"; then
    PGADMIN_OK=true
fi

echo ""

# Open browser function for WSL
open_in_browser() {
    local url=$1
    local name=$2
    
    echo "Opening $name..."
    
    # Try different methods to open browser from WSL
    if command -v explorer.exe &> /dev/null; then
        explorer.exe "$url" &
    elif command -v cmd.exe &> /dev/null; then
        cmd.exe /c start "$url" &
    elif command -v powershell.exe &> /dev/null; then
        powershell.exe -c "Start-Process '$url'" &
    else
        echo "⚠️  Could not open browser automatically"
        echo "   Please open: $url"
    fi
    
    sleep 1
}

# Open services that are running
if [ "$FRONTEND_OK" = true ]; then
    open_in_browser "$FRONTEND_URL" "Frontend Application"
fi

if [ "$BACKEND_OK" = true ]; then
    open_in_browser "$API_DOCS_URL" "API Documentation"
fi

if [ "$PGADMIN_OK" = true ]; then
    open_in_browser "$PGADMIN_URL" "Database Admin (pgAdmin)"
fi

# If nothing is running, provide helpful instructions
if [ "$FRONTEND_OK" = false ] && [ "$BACKEND_OK" = false ] && [ "$PGADMIN_OK" = false ]; then
    echo ""
    echo "❌ No services appear to be running!"
    echo ""
    echo "💡 To start the development environment:"
    echo "   ./scripts/dev-setup.sh"
    echo ""
    echo "📋 Or start services manually:"
    echo "   docker-compose up -d"
    exit 1
fi

echo ""
echo "🎉 Browser windows should now be open!"
echo ""
echo "📍 Service URLs:"
if [ "$FRONTEND_OK" = true ]; then
    echo "   Frontend:    $FRONTEND_URL"
fi
if [ "$BACKEND_OK" = true ]; then
    echo "   Backend API: $BACKEND_URL"
    echo "   API Docs:    $API_DOCS_URL"
fi
if [ "$PGADMIN_OK" = true ]; then
    echo "   Database:    $PGADMIN_URL (admin@kairos.dev / admin)"
fi

echo ""
echo "💡 Tip: Bookmark these URLs for quick access!"