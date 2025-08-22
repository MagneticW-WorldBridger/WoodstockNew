# 🚀 DEPLOY LOFT CHAT TO RAILWAY

## Services

Backend (FastAPI)
- Root directory: backend
- Builder: Nixpacks (Python)
- Build command: pip install -r requirements.txt
- Start command: uvicorn main:app --host 0.0.0.0 --port $PORT
- Healthcheck path: /health
- Env:
  - OPENAI_API_KEY: <copy from .env>
  - OPENAI_MODEL: gpt-4.1
  - DATABASE_URL: <copy from .env>
  - WOODSTOCK_API_BASE: https://api.woodstockoutlet.com/public/index.php/april
  - BACKEND_HOST: 0.0.0.0
  - BACKEND_PORT: $PORT

Frontend (Python static server)
- Root directory: frontend
- Builder: Nixpacks (Python)
- Build command: pip install -r requirements.txt
- Start command: python server.py
- Env:
  - BACKEND_URL: https://<backend-public-domain>

Notes
- We added runtime.txt in both services to ensure Python is present.
- BACKEND_URL must include https:// prefix.

