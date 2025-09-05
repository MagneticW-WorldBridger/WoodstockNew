#!/bin/bash

# LOFT Chat Startup Script
# This script starts both backend and frontend servers

echo "🚀 Starting LOFT Chat System..."
echo "================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -i :$port >/dev/null 2>&1; then
        echo -e "${RED}❌ Port $port is already in use${NC}"
        echo "💡 Run: lsof -i :$port to see what's using it"
        return 1
    fi
    return 0
}

# Function to wait for service
wait_for_service() {
    local url=$1
    local name=$2
    local max_attempts=30
    local attempt=1
    
    echo -e "${YELLOW}⏳ Waiting for $name...${NC}"
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" >/dev/null 2>&1; then
            echo -e "${GREEN}✅ $name is ready!${NC}"
            return 0
        fi
        sleep 1
        attempt=$((attempt + 1))
        echo -ne "${YELLOW}.${NC}"
    done
    
    echo -e "${RED}❌ $name failed to start after $max_attempts seconds${NC}"
    return 1
}

# Check required ports
echo -e "${BLUE}🔍 Checking ports...${NC}"
if ! check_port 8001; then
    echo "🛑 Backend port 8001 is busy. Kill processes and try again."
    exit 1
fi

if ! check_port 3000; then
    echo "🛑 Frontend port 3000 is busy. Kill processes and try again."
    exit 1
fi

# Start backend
echo -e "${PURPLE}🔧 Starting Backend (FastAPI + PydanticAI)...${NC}"
cd backend
source ../venv/bin/activate
python main.py &
BACKEND_PID=$!
echo "📦 Backend PID: $BACKEND_PID"

# Wait for backend to be ready
if ! wait_for_service "http://localhost:8001/health" "Backend"; then
    echo -e "${RED}❌ Backend failed to start${NC}"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

# Start frontend
cd ../frontend
echo -e "${CYAN}🎨 Starting Frontend (Glassmorphism UI)...${NC}"
python3 server.py &
FRONTEND_PID=$!
echo "🖥️ Frontend PID: $FRONTEND_PID"

# Wait for frontend
if ! wait_for_service "http://localhost:3000" "Frontend"; then
    echo -e "${RED}❌ Frontend failed to start${NC}"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 1
fi

echo ""
echo -e "${GREEN}🎉 LOFT Chat System is READY!${NC}"
echo "================================"
echo -e "${CYAN}🔧 Backend API:${NC} http://localhost:8001"
echo -e "${CYAN}🎨 Frontend UI:${NC} http://localhost:3000"
echo -e "${CYAN}📚 API Docs:${NC} http://localhost:8001/docs"
echo ""
echo -e "${YELLOW}💡 Usage Examples:${NC}"
echo "• Find customer with phone 407-288-6040"
echo "• Search for customer email john@example.com"
echo "• Get orders for customer ID 12345"
echo "• Show order details for order 67890"
echo "• Search products containing shirt"
echo ""
echo -e "${PURPLE}🛑 To stop: Press Ctrl+C or run:${NC} kill $BACKEND_PID $FRONTEND_PID"
echo ""

# Create PID file for easy cleanup
echo "$BACKEND_PID $FRONTEND_PID" > ../loft-chat.pids

# Keep script running and handle cleanup
cleanup() {
    echo -e "\n${YELLOW}🛑 Shutting down LOFT Chat...${NC}"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    rm -f ../loft-chat.pids
    echo -e "${GREEN}✅ LOFT Chat stopped cleanly${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Wait for processes
wait
