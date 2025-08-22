# 🚀 DEPLOY LOFT CHAT TO RAILWAY

## 🔥 **DEPLOYMENT STEPS:**

### 1. **Install Railway CLI:**
```bash
npm install -g @railway/cli
```

### 2. **Login to Railway:**
```bash
railway login
```

### 3. **Initialize Project:**
```bash
railway init
```

### 4. **Add PostgreSQL Database:**
```bash
railway add -d postgres
```

### 5. **Deploy:**
```bash
railway up -d
```

### 6. **Set Environment Variables:**
- OPENAI_API_KEY: [Your OpenAI API Key]
- OPENAI_MODEL: gpt-4.1
- DATABASE_URL: ${{Postgres.DATABASE_URL}}
- WOODSTOCK_API_BASE: https://api.woodstockoutlet.com/public/index.php/april

### 7. **Generate Domain:**
```bash
railway domain
```

## ✅ **READY FOR PRODUCTION!**

**Features:**
- 🤖 GPT-4.1 AI Agent
- 🛒 12 LOFT Functions
- 💾 PostgreSQL Memory
- 🎨 Woodstock Design
- 📱 Mobile Responsive
- ⚡ Real-time Streaming

