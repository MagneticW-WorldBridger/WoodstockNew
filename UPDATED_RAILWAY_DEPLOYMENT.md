# 🚀 UPDATED RAILWAY DEPLOYMENT - OCTOBER 2025
## **Current Actual Configuration** ✅

**Last Updated:** October 1, 2025  
**Status:** ✅ **READY FOR DEPLOYMENT**  
**Based on:** Real codebase analysis (not outdated docs)

---

## 📁 **ACTUAL PROJECT STRUCTURE:**
```
loft-chat-chingon/
├── railway.json                    # Root config ✅
├── backend/
│   ├── railway.json               # ✅ READY
│   ├── Procfile                   # ✅ READY
│   ├── requirements.txt           # ✅ READY
│   ├── runtime.txt               # ✅ READY
│   └── main.py                   # ✅ READY
└── frontend/
    ├── railway.json              # ✅ READY
    ├── Procfile                  # ✅ READY
    ├── runtime.txt              # ✅ READY
    └── server.py                # ✅ READY
```

---

## 🔧 **ACTUAL BACKEND CONFIGURATION:**
```json
{
  "$schema": "https://railway.com/railway.schema.json",
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "pip install -r requirements.txt"
  },
  "deploy": {
    "startCommand": "uvicorn main:app --host 0.0.0.0 --port $PORT",
    "numReplicas": 1,
    "sleepApplication": false,
    "restartPolicyType": "ON_FAILURE"
  }
}
```

### **Backend Procfile:**
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

### **Backend Dependencies:**
```
fastapi[all]==0.115.7
uvicorn[standard]==0.35.0
pydantic-ai-slim[openai]==0.0.49
pydantic-ai-slim[mcp]==0.0.49
openai>=1.67.0
httpx==0.28.1
python-dotenv==1.0.0
sqlite-utils==3.38
asyncpg==0.29.0
mcp>=1.0.0
```

---

## 🎨 **ACTUAL FRONTEND CONFIGURATION:**
```json
{
  "$schema": "https://railway.com/railway.schema.json", 
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python server.py",
    "numReplicas": 1,
    "sleepApplication": false,
    "restartPolicyType": "ON_FAILURE"
  }
}
```

### **Frontend Procfile:**
```
web: python server.py
```

### **Frontend Server Features:**
- ✅ Dynamic `BACKEND_URL` injection via `/env.js`
- ✅ CORS headers for development
- ✅ Auto-detects `PORT` from Railway environment
- ✅ Production-ready static file serving

---

## 🔑 **REQUIRED ENVIRONMENT VARIABLES:**

### **Backend Service:**
```bash
# ESSENTIAL (MUST SET)
OPENAI_API_KEY=sk-proj-[your-key]
OPENAI_MODEL=gpt-4.1
DATABASE_URL=postgres://[neon-db-connection]

# WOODSTOCK APIs (FROM CURRENT .ENV)
WOODSTOCK_API_BASE=https://api.woodstockoutlet.com/public/index.php/april

# MAGENTO API (MISSING - NEED TO ADD)
MAGENTO_API_BASE=https://woodstockoutlet.com
MAGENTO_ADMIN_TOKEN=[your-token]

# SOCIAL INTEGRATIONS (FROM .ENV)
FACEBOOK_APP_ID=1580245996190079
FACEBOOK_PAGE_ACCESS_TOKEN=[current-token]

# VAPI (PHONE INTEGRATION)
VAPI_PRIVATE_KEY=b5300c16-3daf-4e11-bbf7-9340330c568a
VAPI_ASSISTANT_ID=c87873cc-5fdc-41bf-a5fb-598534df09a2
VAPI_PHONE_NUMBER=b1449398-ebe2-4c6c-9771-7457a95a835a

# PRODUCTION SETTINGS
RAILWAY_ENVIRONMENT=production
```

### **Frontend Service:**
```bash
BACKEND_URL=https://[backend-service-url].railway.app
PORT=3000
RAILWAY_ENVIRONMENT=production
```

---

## 🚀 **DEPLOYMENT STEPS:**

### **PHASE 1: GITHUB PUSH**
```bash
cd loft-chat-chingon
git add .
git commit -m "🚀 READY FOR RAILWAY DEPLOYMENT - All configs updated"
git push origin main
```

### **PHASE 2: RAILWAY BACKEND**
1. **Go to Railway Dashboard**
2. **Select Backend Service**
3. **Settings → Service Settings:**
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements.txt` 
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

4. **Add Environment Variables** (copy from list above)
5. **Deploy**

### **PHASE 3: RAILWAY FRONTEND**  
1. **Select Frontend Service**
2. **Settings → Service Settings:**
   - Root Directory: `frontend`
   - Start Command: `python server.py`

3. **Environment Variables:**
   ```
   BACKEND_URL = https://[backend-url].railway.app
   PORT = 3000
   ```

4. **Generate Domain** and **Deploy**

---

## ✅ **CRITICAL DIFFERENCES FROM OLD DOCS:**
1. **Real file structure** (not hypothetical)
2. **Actual Railway configs** exist and are correct
3. **Current dependencies** match working system
4. **Environment variables** from real `.env` file
5. **VAPI credentials** ready for phone integration
6. **MCP integration** included in requirements

---

## 🎯 **POST-DEPLOYMENT VALIDATION:**
```bash
# Backend health check
curl https://[backend-url].railway.app/health

# Frontend check  
curl https://[frontend-url].railway.app

# Full system test
# Visit frontend URL and test customer lookup
```

---

## 🔥 **MISSING PIECES (NEED USER INPUT):**
1. **MAGENTO_ADMIN_TOKEN** - Not in current .env
2. **Railway project name/URLs** - Need current info
3. **GitHub repository URL** - For connecting Railway

**Status:** 🚀 **READY TO DEPLOY - NEED USER CONFIRMATION**

