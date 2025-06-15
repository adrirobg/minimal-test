#!/bin/bash
# WSL-Optimized Development Logs Script - Easy log viewing for debugging

set -e

echo "📋 Kairos BCP - WSL Development Logs"
echo "===================================="

# WSL Environment Check
if ! docker ps &> /dev/null; then
    echo "🔧 Starting Docker service..."
    sudo service docker start
    sleep 2
fi

# Function to show usage
show_usage() {
    echo "Usage: $0 [service] [options]"
    echo ""
    echo "Services:"
    echo "   all        - All services (default)"
    echo "   backend    - Backend API logs"
    echo "   frontend   - Frontend application logs"
    echo "   postgres   - PostgreSQL database logs"
    echo "   pgadmin    - pgAdmin interface logs"
    echo ""
    echo "Options:"
    echo "   -f, --follow    - Follow logs in real-time"
    echo "   -t, --tail N    - Show last N lines (default: 50)"
    echo "   -h, --help      - Show this help"
    echo ""
    echo "Examples:"
    echo "   $0                    # Show all logs (last 50 lines)"
    echo "   $0 backend -f         # Follow backend logs"
    echo "   $0 frontend -t 100    # Show last 100 frontend logs"
    echo "   $0 postgres           # Show PostgreSQL logs"
}

# Parse arguments
SERVICE="all"
FOLLOW=""
TAIL="50"

while [[ $# -gt 0 ]]; do
    case $1 in
        backend|frontend|postgres|pgadmin|all)
            SERVICE="$1"
            shift
            ;;
        -f|--follow)
            FOLLOW="-f"
            shift
            ;;
        -t|--tail)
            TAIL="$2"
            shift 2
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            echo "❌ Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Check if services are running
if ! docker-compose ps | grep -q "Up"; then
    echo "❌ No services are running!"
    echo "   Start them with: docker-compose up -d"
    exit 1
fi

# Show service status
echo "📊 Service Status:"
docker-compose ps
echo ""

# Build docker-compose logs command
CMD="docker-compose logs"

if [[ -n "$FOLLOW" ]]; then
    CMD="$CMD $FOLLOW"
else
    CMD="$CMD --tail=$TAIL"
fi

if [[ "$SERVICE" != "all" ]]; then
    CMD="$CMD $SERVICE"
fi

# Show logs
case $SERVICE in
    all)
        echo "📋 Showing logs for all services..."
        if [[ -n "$FOLLOW" ]]; then
            echo "   (Press Ctrl+C to stop following)"
        fi
        ;;
    backend)
        echo "🔧 Showing backend API logs..."
        ;;
    frontend)
        echo "📱 Showing frontend application logs..."
        ;;
    postgres)
        echo "💾 Showing PostgreSQL database logs..."
        ;;
    pgadmin)
        echo "🔍 Showing pgAdmin interface logs..."
        ;;
esac

echo ""
echo "----------------------------------------"

# WSL-specific tip
if [[ -n "$FOLLOW" ]]; then
    echo "💡 WSL Tip: Use VS Code integrated terminal for better log viewing experience"
    echo "   Press Ctrl+C to stop following logs"
fi

echo ""

# Execute the command
exec $CMD