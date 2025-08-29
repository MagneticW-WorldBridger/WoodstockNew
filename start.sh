#!/bin/bash
set -e

echo "🚀 Starting LOFT Chat Backend..."

# For Railway: Start backend directly (MCP optional)
# If MCP_ENABLE=true, start supergateway first
if [ "${MCP_ENABLE}" = "true" ]; then
    echo "🔌 Starting MCP Supergateway..."
    npx -y supergateway \
        --sse "https://mcp.pipedream.net/811da2de-2d54-40e4-9d92-050d7306328d/google_calendar" \
        --outputTransport sse \
        --port 3333 &
    
    echo "⏳ Waiting for MCP Gateway to initialize..."
    sleep 5
fi

# Start the FastAPI backend
echo "🚀 Starting FastAPI Backend..."
cd backend
uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
