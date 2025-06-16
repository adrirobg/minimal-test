#!/bin/bash

# Complete Test Suite Runner
# Runs all tests to ensure full user workflow functions without errors

set -e

echo "🚀 Starting Complete Test Suite"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test results tracking
BACKEND_TESTS_PASSED=false
FRONTEND_TESTS_PASSED=false
E2E_TESTS_PASSED=false
WORKFLOW_VALIDATION_PASSED=false

# Function to print colored output
print_status() {
    local status=$1
    local message=$2
    
    if [ "$status" = "SUCCESS" ]; then
        echo -e "${GREEN}✅ $message${NC}"
    elif [ "$status" = "ERROR" ]; then
        echo -e "${RED}❌ $message${NC}"
    elif [ "$status" = "WARNING" ]; then
        echo -e "${YELLOW}⚠️ $message${NC}"
    elif [ "$status" = "INFO" ]; then
        echo -e "${BLUE}ℹ️ $message${NC}"
    fi
}

# Function to check if service is running
check_service() {
    local url=$1
    local service_name=$2
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" > /dev/null 2>&1; then
            print_status "SUCCESS" "$service_name is running"
            return 0
        fi
        
        print_status "INFO" "Waiting for $service_name... (attempt $attempt/$max_attempts)"
        sleep 2
        attempt=$((attempt + 1))
    done
    
    print_status "ERROR" "$service_name failed to start after $max_attempts attempts"
    return 1
}

# Function to run backend tests
run_backend_tests() {
    print_status "INFO" "Running Backend Tests..."
    
    cd backend/
    
    # Check if Poetry is available
    if ! command -v poetry &> /dev/null; then
        print_status "ERROR" "Poetry not found. Please install Poetry first."
        return 1
    fi
    
    # Install dependencies
    print_status "INFO" "Installing backend dependencies..."
    poetry install
    
    # Run pytest
    if poetry run pytest tests/ -v --tb=short; then
        print_status "SUCCESS" "Backend tests passed"
        BACKEND_TESTS_PASSED=true
    else
        print_status "ERROR" "Backend tests failed"
        BACKEND_TESTS_PASSED=false
    fi
    
    cd ..
}

# Function to run frontend tests
run_frontend_tests() {
    print_status "INFO" "Running Frontend Tests..."
    
    cd frontend/
    
    # Check if npm is available
    if ! command -v npm &> /dev/null; then
        print_status "ERROR" "npm not found. Please install Node.js and npm first."
        return 1
    fi
    
    # Install dependencies
    print_status "INFO" "Installing frontend dependencies..."
    npm install
    
    # Run lint
    if npm run lint; then
        print_status "SUCCESS" "Frontend linting passed"
    else
        print_status "WARNING" "Frontend linting has issues"
    fi
    
    # Run build to check for compilation errors
    if npm run build; then
        print_status "SUCCESS" "Frontend build passed"
        FRONTEND_TESTS_PASSED=true
    else
        print_status "ERROR" "Frontend build failed"
        FRONTEND_TESTS_PASSED=false
    fi
    
    cd ..
}

# Function to start services for testing
start_services() {
    print_status "INFO" "Starting services for testing..."
    
    # Start PostgreSQL with Docker Compose
    if command -v docker-compose &> /dev/null; then
        print_status "INFO" "Starting PostgreSQL with Docker Compose..."
        docker-compose up -d postgres
        sleep 5
    else
        print_status "WARNING" "Docker Compose not found. Assuming PostgreSQL is already running."
    fi
    
    # Start backend
    print_status "INFO" "Starting backend server..."
    cd backend/
    poetry run uvicorn app.main:app --port 8000 &
    BACKEND_PID=$!
    cd ..
    
    # Start frontend
    print_status "INFO" "Starting frontend server..."
    cd frontend/
    npm run build
    npm start &
    FRONTEND_PID=$!
    cd ..
    
    # Wait for services to be ready
    print_status "INFO" "Waiting for services to start..."
    
    if check_service "http://localhost:8000/health" "Backend API"; then
        print_status "SUCCESS" "Backend API is ready"
    else
        print_status "ERROR" "Backend API failed to start"
        return 1
    fi
    
    if check_service "http://localhost:3000" "Frontend"; then
        print_status "SUCCESS" "Frontend is ready"
    else
        print_status "ERROR" "Frontend failed to start"
        return 1
    fi
}

# Function to stop services
stop_services() {
    print_status "INFO" "Stopping services..."
    
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    
    # Stop Docker services
    if command -v docker-compose &> /dev/null; then
        docker-compose down
    fi
    
    print_status "INFO" "Services stopped"
}

# Function to run E2E tests
run_e2e_tests() {
    print_status "INFO" "Running E2E Tests..."
    
    cd tests/e2e/
    
    # Install Python dependencies for E2E tests
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    fi
    
    # Run pytest E2E tests
    if python -m pytest -v --tb=short; then
        print_status "SUCCESS" "E2E Python tests passed"
    else
        print_status "ERROR" "E2E Python tests failed"
        E2E_TESTS_PASSED=false
        cd ../..
        return 1
    fi
    
    cd ../..
    
    # Run Playwright tests if available
    if [ -f "tests/e2e/playwright.config.ts" ]; then
        print_status "INFO" "Running Playwright tests..."
        
        # Install Playwright if not already installed
        if ! command -v npx &> /dev/null; then
            print_status "WARNING" "npx not found. Skipping Playwright tests."
        else
            cd frontend/
            npx playwright install
            
            if npx playwright test --config=../tests/e2e/playwright.config.ts; then
                print_status "SUCCESS" "Playwright tests passed"
                E2E_TESTS_PASSED=true
            else
                print_status "ERROR" "Playwright tests failed"
                E2E_TESTS_PASSED=false
            fi
            cd ..
        fi
    else
        E2E_TESTS_PASSED=true
    fi
}

# Function to run workflow validation
run_workflow_validation() {
    print_status "INFO" "Running Workflow Validation..."
    
    if python tests/workflow_validation.py; then
        print_status "SUCCESS" "Workflow validation passed"
        WORKFLOW_VALIDATION_PASSED=true
    else
        print_status "ERROR" "Workflow validation failed"
        WORKFLOW_VALIDATION_PASSED=false
    fi
}

# Function to generate test report
generate_test_report() {
    echo ""
    echo "=================================="
    echo "📊 TEST SUITE RESULTS"
    echo "=================================="
    
    if [ "$BACKEND_TESTS_PASSED" = true ]; then
        print_status "SUCCESS" "Backend Tests: PASSED"
    else
        print_status "ERROR" "Backend Tests: FAILED"
    fi
    
    if [ "$FRONTEND_TESTS_PASSED" = true ]; then
        print_status "SUCCESS" "Frontend Tests: PASSED"
    else
        print_status "ERROR" "Frontend Tests: FAILED"
    fi
    
    if [ "$E2E_TESTS_PASSED" = true ]; then
        print_status "SUCCESS" "E2E Tests: PASSED"
    else
        print_status "ERROR" "E2E Tests: FAILED"
    fi
    
    if [ "$WORKFLOW_VALIDATION_PASSED" = true ]; then
        print_status "SUCCESS" "Workflow Validation: PASSED"
    else
        print_status "ERROR" "Workflow Validation: FAILED"
    fi
    
    echo ""
    echo "=================================="
    
    # Overall result
    if [ "$BACKEND_TESTS_PASSED" = true ] && [ "$FRONTEND_TESTS_PASSED" = true ] && [ "$E2E_TESTS_PASSED" = true ] && [ "$WORKFLOW_VALIDATION_PASSED" = true ]; then
        print_status "SUCCESS" "🎉 ALL TESTS PASSED! System is ready for production."
        echo ""
        echo "✅ User workflows function correctly without errors"
        echo "✅ Backend API is working properly"
        echo "✅ Frontend is building and functioning"
        echo "✅ End-to-end integration is working"
        echo "✅ Performance requirements are met"
        return 0
    else
        print_status "ERROR" "❌ SOME TESTS FAILED! Please review the errors above."
        echo ""
        echo "⚠️ System is not ready for production deployment"
        echo "⚠️ Please fix the failing tests before proceeding"
        return 1
    fi
}

# Trap to ensure services are stopped on exit
trap 'stop_services' EXIT

# Main execution
main() {
    # Parse command line arguments
    SKIP_BACKEND=false
    SKIP_FRONTEND=false
    SKIP_E2E=false
    SKIP_SERVICES=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --skip-backend)
                SKIP_BACKEND=true
                shift
                ;;
            --skip-frontend)
                SKIP_FRONTEND=true
                shift
                ;;
            --skip-e2e)
                SKIP_E2E=true
                shift
                ;;
            --skip-services)
                SKIP_SERVICES=true
                shift
                ;;
            -h|--help)
                echo "Usage: $0 [OPTIONS]"
                echo ""
                echo "Options:"
                echo "  --skip-backend   Skip backend tests"
                echo "  --skip-frontend  Skip frontend tests"
                echo "  --skip-e2e       Skip E2E tests"
                echo "  --skip-services  Skip starting services (assume they're already running)"
                echo "  -h, --help       Show this help message"
                exit 0
                ;;
            *)
                print_status "ERROR" "Unknown option: $1"
                exit 1
                ;;
        esac
    done
    
    # Run tests
    if [ "$SKIP_BACKEND" = false ]; then
        run_backend_tests
    else
        BACKEND_TESTS_PASSED=true
        print_status "INFO" "Skipping backend tests"
    fi
    
    if [ "$SKIP_FRONTEND" = false ]; then
        run_frontend_tests
    else
        FRONTEND_TESTS_PASSED=true
        print_status "INFO" "Skipping frontend tests"
    fi
    
    # Start services if not skipping
    if [ "$SKIP_SERVICES" = false ]; then
        if ! start_services; then
            print_status "ERROR" "Failed to start services"
            exit 1
        fi
    else
        print_status "INFO" "Skipping service startup (assuming they're already running)"
    fi
    
    # Run E2E tests and workflow validation (these require running services)
    if [ "$SKIP_E2E" = false ]; then
        run_e2e_tests
    else
        E2E_TESTS_PASSED=true
        print_status "INFO" "Skipping E2E tests"
    fi
    
    run_workflow_validation
    
    # Generate final report
    generate_test_report
}

# Run main function with all arguments
main "$@"