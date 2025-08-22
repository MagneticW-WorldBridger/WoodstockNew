#!/bin/bash

# LOFT Chat with Memory - Startup Script
echo "🧠 Starting LOFT Chat with MEMORY..."
echo "================================"

# Kill any existing processes
echo "🔫 Killing existing processes..."
pkill -f "python.*main" 2>/dev/null || true
pkill -f "python.*server" 2>/dev/null || true

# Wait a moment
sleep 2

# Change to project directory
cd "$(dirname "$0")"

# Activate virtual environment
echo "🔧 Activating Python environment..."
source venv/bin/activate

# Start backend with memory
echo "🚀 Starting Backend with Memory..."
cd backend
python main.py &
BACKEND_PID=$!
echo "📦 Backend PID: $BACKEND_PID"

# Wait for backend to start
echo "⏳ Waiting for Backend..."
sleep 5

# Start frontend
echo "🎨 Starting Frontend..."
cd ../frontend
python3 server.py &
FRONTEND_PID=$!
echo "🖥️ Frontend PID: $FRONTEND_PID"

# Wait for frontend
sleep 3

echo ""
echo "🎉 LOFT Chat with MEMORY is READY!"
echo "================================"
echo "🔧 Backend API: http://localhost:8001"
echo "🎨 Frontend UI: http://localhost:3000"
echo "📚 API Docs: http://localhost:8001/docs"
echo ""
echo "💡 Test conversation memory:"
echo "1. Say: '407-288-6040' (finds Janice)"
echo "2. Then: 'What are my orders?' (remembers you're Janice!)"
echo ""
echo "🛑 To stop: Ctrl+C or run: ./stop-memory-chat.sh"

# Open browser
sleep 2
open http://localhost:3000 2>/dev/null || true

# Save PIDs for cleanup
echo "$BACKEND_PID $FRONTEND_PID" > .loft_memory_pids

# Wait for user interrupt
trap "echo '🛑 Stopping services...' && kill $BACKEND_PID $FRONTEND_PID 2>/dev/null && rm -f .loft_memory_pids && echo '✅ Services stopped'" EXIT

wait
