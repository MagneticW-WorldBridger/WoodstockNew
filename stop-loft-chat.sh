#!/bin/bash

# LOFT Chat Stop Script
# Kills all LOFT Chat processes cleanly

echo "🛑 Stopping LOFT Chat System..."

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Kill by PID file if exists
if [ -f "loft-chat.pids" ]; then
    echo -e "${YELLOW}📁 Reading PID file...${NC}"
    PIDS=$(cat loft-chat.pids)
    echo "🔍 Found PIDs: $PIDS"
    
    for pid in $PIDS; do
        if kill -0 $pid 2>/dev/null; then
            echo -e "${YELLOW}🔫 Killing PID $pid...${NC}"
            kill $pid
        else
            echo -e "${RED}❌ PID $pid not running${NC}"
        fi
    done
    
    rm loft-chat.pids
    echo -e "${GREEN}✅ PID file cleaned${NC}"
fi

# Kill by process name (backup method)
echo -e "${YELLOW}🔍 Killing remaining processes...${NC}"

# Kill Python backend processes
BACKEND_PIDS=$(pgrep -f "python.*main.py")
if [ ! -z "$BACKEND_PIDS" ]; then
    echo "🔫 Killing backend processes: $BACKEND_PIDS"
    echo $BACKEND_PIDS | xargs kill
fi

# Kill Python frontend processes  
FRONTEND_PIDS=$(pgrep -f "python.*server.py")
if [ ! -z "$FRONTEND_PIDS" ]; then
    echo "🔫 Killing frontend processes: $FRONTEND_PIDS"
    echo $FRONTEND_PIDS | xargs kill
fi

# Check ports
echo -e "${YELLOW}🔍 Checking ports...${NC}"

if lsof -i :8001 >/dev/null 2>&1; then
    echo -e "${RED}⚠️ Port 8001 still in use:${NC}"
    lsof -i :8001
    BACKEND_PID=$(lsof -ti :8001)
    if [ ! -z "$BACKEND_PID" ]; then
        echo "🔫 Force killing port 8001 processes..."
        kill -9 $BACKEND_PID 2>/dev/null
    fi
else
    echo -e "${GREEN}✅ Port 8001 is free${NC}"
fi

if lsof -i :3000 >/dev/null 2>&1; then
    echo -e "${RED}⚠️ Port 3000 still in use:${NC}"
    lsof -i :3000
    FRONTEND_PID=$(lsof -ti :3000)
    if [ ! -z "$FRONTEND_PID" ]; then
        echo "🔫 Force killing port 3000 processes..."
        kill -9 $FRONTEND_PID 2>/dev/null
    fi
else
    echo -e "${GREEN}✅ Port 3000 is free${NC}"
fi

echo ""
echo -e "${GREEN}🎉 LOFT Chat System stopped cleanly!${NC}"
echo -e "${CYAN}💡 To restart: ./start-loft-chat.sh${NC}"
