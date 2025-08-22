#!/usr/bin/env python3
"""
LOFT Chat - Combined Frontend + Backend Server
Serves both the FastAPI backend and static frontend files
"""

import os
import sys
import uvicorn
from pathlib import Path

# Add backend to Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from backend.main import app
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, Response
from fastapi import HTTPException

# Mount frontend static files
frontend_dir = Path(__file__).parent / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

# Serve frontend files directly
@app.get("/style.css")
async def get_css():
    css_path = frontend_dir / "style.css"
    if css_path.exists():
        with open(css_path, "r") as f:
            return Response(content=f.read(), media_type="text/css")
    raise HTTPException(status_code=404, detail="CSS not found")

@app.get("/script.js")
async def get_js():
    js_path = frontend_dir / "script.js"
    if js_path.exists():
        with open(js_path, "r") as f:
            js_content = f.read()
            # Fix API base for production
            js_content = js_content.replace(
                "this.apiBase = 'http://localhost:8001';",
                "this.apiBase = window.location.origin;"
            )
            return Response(content=js_content, media_type="application/javascript")
    raise HTTPException(status_code=404, detail="JS not found")

# Override root route to serve chat frontend
@app.get("/", response_class=HTMLResponse)
async def serve_chat():
    """Serve the main chat interface"""
    html_path = frontend_dir / "index.html"
    if html_path.exists():
        with open(html_path, "r") as f:
            return f.read()
    
    return """
    <html>
        <head>
            <title>🚀 LOFT Chat - Production</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #002147; color: white; text-align: center; }
                .container { max-width: 600px; margin: 0 auto; padding: 30px; }
                h1 { color: #E63946; }
                .status { background: #28a745; color: white; padding: 10px; border-radius: 5px; margin: 20px 0; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🚀 LOFT Chat v2.0</h1>
                <div class="status">✅ Backend API is running!</div>
                <p>Frontend files not found. Check deployment.</p>
                <p><strong>API Docs:</strong> <a href="/docs" style="color: #E63946;">/docs</a></p>
            </div>
        </body>
    </html>
    """

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
