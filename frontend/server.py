#!/usr/bin/env python3
"""Simple HTTP server for LOFT Chat frontend"""

import http.server
import socketserver
import webbrowser
import os
import sys
from pathlib import Path

PORT = 3000
FRONTEND_DIR = Path(__file__).parent


class LoftChatHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler for LOFT Chat frontend"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(FRONTEND_DIR), **kwargs)
    
    def end_headers(self):
        # CORS headers for development
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        # Cache control
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        super().end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()
    
    def log_message(self, format, *args):
        # Custom logging
        print(f"🌐 {self.address_string()} - {format % args}")


def start_server():
    """Start the LOFT Chat frontend server"""
    
    # Change to frontend directory
    os.chdir(FRONTEND_DIR)
    
    try:
        with socketserver.TCPServer(("", PORT), LoftChatHandler) as httpd:
            print("🚀 LOFT Chat Frontend Server Starting...")
            print(f"📱 Serving at: http://localhost:{PORT}")
            print(f"📁 Directory: {FRONTEND_DIR}")
            print("🔧 Backend should be running on: http://localhost:8001")
            print("\n🎯 Opening browser in 2 seconds...")
            print("💡 Press Ctrl+C to stop server\n")
            
            # Open browser after a short delay
            import threading
            def open_browser():
                import time
                time.sleep(2)
                webbrowser.open(f'http://localhost:{PORT}')
            
            browser_thread = threading.Thread(target=open_browser, daemon=True)
            browser_thread.start()
            
            # Start server
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        sys.exit(0)
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"❌ Port {PORT} is already in use!")
            print("💡 Try: lsof -i :3000 to see what's using it")
            sys.exit(1)
        else:
            print(f"❌ Server error: {e}")
            sys.exit(1)


if __name__ == "__main__":
    start_server()
