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

# Frontend directory path
frontend_dir = Path(__file__).parent / "frontend"
print(f"🔧 Frontend directory: {frontend_dir}")
print(f"🔧 Frontend exists: {frontend_dir.exists()}")
if frontend_dir.exists():
    print(f"🔧 Frontend files: {list(frontend_dir.glob('*'))}")

# Only mount if directory exists
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
    print(f"🔧 Looking for HTML at: {html_path}")
    print(f"🔧 HTML exists: {html_path.exists()}")
    
    if html_path.exists():
        with open(html_path, "r") as f:
            return f.read()
    
    # Debug info for troubleshooting
    current_dir = Path(__file__).parent
    all_files = list(current_dir.rglob("*"))
    
    return f"""
    <html>
        <head>
            <title>🚀 LOFT Chat - Production Debug</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background: #002147; color: white; }}
                .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
                h1 {{ color: #E63946; }}
                .status {{ background: #28a745; color: white; padding: 10px; border-radius: 5px; margin: 20px 0; }}
                .debug {{ background: #333; padding: 15px; border-radius: 5px; margin: 10px 0; font-family: monospace; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🚀 LOFT Chat v2.0 - Debug</h1>
                <div class="status">✅ Backend API is running!</div>
                
                <div class="debug">
                    <h3>🔧 Debug Info:</h3>
                    <p><strong>Current Dir:</strong> {current_dir}</p>
                    <p><strong>Frontend Dir:</strong> {frontend_dir}</p>
                    <p><strong>Frontend Exists:</strong> {frontend_dir.exists()}</p>
                    <p><strong>All Files:</strong><br>
                    {'<br>'.join([str(f) for f in all_files[:20]])}
                    {f'<br>... and {len(all_files)-20} more files' if len(all_files) > 20 else ''}
                    </p>
                </div>
                
                <p><strong>API Docs:</strong> <a href="/docs" style="color: #E63946;">/docs</a></p>
                <p><strong>Chat API:</strong> <a href="/v1/chat/completions" style="color: #E63946;">/v1/chat/completions</a></p>
            </div>
        </body>
    </html>
    """

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
