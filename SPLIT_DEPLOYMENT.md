# 🚀 SPLIT DEPLOYMENT GUIDE

## Overview

This project is designed for **separate frontend and backend deployment**. They communicate via HTTP API and can be hosted on different platforms.

---

## 📦 DEPLOYMENT OPTIONS

### Frontend Deployment Platforms
- **Vercel** (Recommended for Next.js)
- Netlify
- Cloudflare Pages
- AWS Amplify

### Backend Deployment Platforms
- **Railway** (Recommended for Python)
- Render
- Fly.io
- Google Cloud Run
- AWS App Runner
- DigitalOcean App Platform

---

## 🎯 DEPLOYMENT ARCHITECTURE

```
┌─────────────────────┐           ┌─────────────────────┐
│   Frontend (Next.js)│           │  Backend (FastAPI)  │
│   ─────────────────│           │  ─────────────────  │
│   - Vercel/Netlify │  HTTP/S  │  - Railway/Render   │
│   - Static assets  │ ◄────────►│  - Python 3.10+     │
│   - UI components  │           │  - API endpoints    │
└─────────────────────┘           └─────────────────────┘
         │                                 │
         │                                 │
         ▼                                 ▼
   Browser Client               ┌──────────────────────┐
   (Public URLs)                │  External Services   │
                                │  ─────────────────── │
                                │  - Qdrant Cloud      │
                                │  - Groq API          │
                                │  - Tavily API        │
                                └──────────────────────┘
```

---

## 📁 FRONTEND DEPLOYMENT

### Files Required
```
app/                    # Next.js pages
components/             # React components
hooks/                  # React hooks
lib/                    # API client & utilities
styles/                 # CSS styles
public/                 # Static assets
package.json            # Dependencies
pnpm-lock.yaml          # Lock file
next.config.mjs         # Next.js config
postcss.config.mjs      # PostCSS config
tsconfig.json           # TypeScript config
components.json         # Shadcn/UI config
.env.frontend.example   # Environment template
```

### Environment Variables (Frontend)
```bash
# .env.local (development)
NEXT_PUBLIC_API_URL=http://localhost:8000

# Production (configure in hosting platform)
NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app
```

### Deployment Steps

#### Option 1: Vercel (Recommended)
```bash
# 1. Install Vercel CLI
npm i -g vercel

# 2. Deploy
vercel

# 3. Set environment variable in Vercel dashboard
# NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app

# 4. Redeploy
vercel --prod
```

#### Option 2: Netlify
```bash
# 1. Install Netlify CLI
npm i -g netlify-cli

# 2. Build
pnpm build

# 3. Deploy
netlify deploy --prod --dir=.next

# 4. Set environment variable in Netlify dashboard
# NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app
```

#### Option 3: Docker
```dockerfile
# Dockerfile.frontend
FROM node:20-alpine

WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN npm install -g pnpm && pnpm install

COPY . .
RUN pnpm build

EXPOSE 3000
CMD ["pnpm", "start"]
```

```bash
docker build -f Dockerfile.frontend -t mnemonic-frontend .
docker run -p 3000:3000 -e NEXT_PUBLIC_API_URL=https://api.yourdomain.com mnemonic-frontend
```

### Build Commands
```bash
# Install dependencies
pnpm install

# Development server
pnpm dev

# Production build
pnpm build

# Start production server
pnpm start
```

### Frontend Verification
```bash
# 1. Check build succeeds
pnpm build

# 2. Verify API connection (in browser console)
fetch(process.env.NEXT_PUBLIC_API_URL + '/health')
  .then(r => r.json())
  .then(console.log)

# Expected output:
# { status: "healthy", qdrant_connected: true, tavily_available: true }
```

---

## 🐍 BACKEND DEPLOYMENT

### Files Required
```
api_server.py           # FastAPI application
src/                    # Core logic
  ├── __init__.py
  ├── config.py
  ├── pipeline.py
  ├── validation.py
  ├── data_ingestion.py
  └── agents/
      ├── __init__.py
      ├── memory.py
      ├── normalizer.py
      ├── reasoner.py
      ├── retriever.py
      └── web_search.py
requirements.txt        # Python dependencies
.env.backend.example    # Environment template
data/                   # Cache directory (empty)
  └── cache/
```

### Environment Variables (Backend)
```bash
# .env (development)
GROQ_API_KEY=gsk_your_key_here
QDRANT_URL=https://xxxxx.us-east4-0.gcp.cloud.qdrant.io
QDRANT_API_KEY=your_qdrant_key_here
TAVILY_API_KEY=tvly_your_key_here  # Optional
CORS_ORIGINS=http://localhost:3000
LOG_LEVEL=INFO

# Production (configure in hosting platform)
GROQ_API_KEY=gsk_production_key
QDRANT_URL=https://xxxxx.us-east4-0.gcp.cloud.qdrant.io
QDRANT_API_KEY=your_qdrant_key
TAVILY_API_KEY=tvly_production_key
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
LOG_LEVEL=WARNING
```

### Deployment Steps

#### Option 1: Railway (Recommended)
```bash
# 1. Install Railway CLI
npm i -g @railway/cli

# 2. Login
railway login

# 3. Initialize project
railway init

# 4. Deploy
railway up

# 5. Set environment variables via Railway dashboard
# Navigate to Variables tab and add all from .env.backend.example

# 6. Get deployment URL
railway domain
```

#### Option 2: Render
```yaml
# render.yaml
services:
  - type: web
    name: mnemonic-backend
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn api_server:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.10.0
      - key: GROQ_API_KEY
        sync: false  # Set in dashboard
      - key: QDRANT_URL
        sync: false
      - key: QDRANT_API_KEY
        sync: false
      - key: TAVILY_API_KEY
        sync: false
      - key: CORS_ORIGINS
        sync: false
      - key: LOG_LEVEL
        value: WARNING
```

#### Option 3: Docker
```dockerfile
# Dockerfile.backend
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY api_server.py .
COPY src/ src/
RUN mkdir -p data/cache

EXPOSE 8000
CMD ["uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -f Dockerfile.backend -t mnemonic-backend .
docker run -p 8000:8000 --env-file .env mnemonic-backend
```

### Build Commands
```bash
# Install dependencies
pip install -r requirements.txt

# Development server (with auto-reload)
uvicorn api_server:app --reload --host 0.0.0.0 --port 8000

# Production server
uvicorn api_server:app --host 0.0.0.0 --port 8000 --workers 4
```

### Backend Verification
```bash
# 1. Check health endpoint
curl https://your-backend-url.railway.app/health

# Expected output:
# {"status":"healthy","qdrant_connected":true,"tavily_available":true}

# 2. Test verification endpoint
curl -X POST https://your-backend-url.railway.app/verify \
  -H "Content-Type: application/json" \
  -d '{"claim": "The Earth is round"}'

# Expected: JSON response with verdict, confidence, explanation
```

---

## 🔗 CONNECTING FRONTEND TO BACKEND

### Step 1: Deploy Backend First
1. Deploy backend to Railway/Render
2. Note the deployment URL (e.g., `https://mnemonic-backend.railway.app`)
3. Verify health endpoint returns `{"status":"healthy"}`

### Step 2: Configure Frontend
1. Set `NEXT_PUBLIC_API_URL` environment variable
2. Deploy frontend to Vercel/Netlify
3. Verify API calls work in browser console

### Step 3: Update Backend CORS
1. Update `CORS_ORIGINS` in backend environment
2. Add your frontend URL (e.g., `https://mnemonic.vercel.app`)
3. Redeploy backend

### Testing Connection
```javascript
// In browser console on deployed frontend
fetch(process.env.NEXT_PUBLIC_API_URL + '/health')
  .then(r => r.json())
  .then(data => {
    if (data.status === 'healthy') {
      console.log('✅ Backend connected successfully!')
    }
  })
```

---

## 🔒 CORS CONFIGURATION

### Development
```python
# Backend: CORS_ORIGINS=http://localhost:3000
# Frontend: NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Production
```python
# Backend: CORS_ORIGINS=https://mnemonic.vercel.app,https://www.mnemonic.vercel.app
# Frontend: NEXT_PUBLIC_API_URL=https://mnemonic-backend.railway.app
```

### Multiple Environments
```python
# Backend supports comma-separated origins:
CORS_ORIGINS=https://prod.example.com,https://staging.example.com,http://localhost:3000
```

---

## 🧪 TESTING SPLIT DEPLOYMENT

### 1. Local Development (Both Running)
```bash
# Terminal 1: Backend
cd backend/
uvicorn api_server:app --reload --port 8000

# Terminal 2: Frontend
cd frontend/
pnpm dev
```

### 2. Backend Deployed, Frontend Local
```bash
# .env.local
NEXT_PUBLIC_API_URL=https://your-backend.railway.app

# Start frontend
pnpm dev
```

### 3. Frontend Deployed, Backend Local
```bash
# Update Vercel environment variable
NEXT_PUBLIC_API_URL=https://your-ngrok-url.ngrok.io

# Start backend with ngrok
ngrok http 8000
uvicorn api_server:app --reload
```

### 4. Both Deployed (Production)
```bash
# Backend: https://mnemonic-backend.railway.app
# Frontend: https://mnemonic.vercel.app
# Both configured with each other's URLs
```

---

## 📊 MONITORING & DEBUGGING

### Frontend Issues
```bash
# Check browser console for errors
# Look for CORS errors, 404s, or connection refused

# Common issues:
# 1. NEXT_PUBLIC_API_URL not set → Check environment variables
# 2. CORS error → Update backend CORS_ORIGINS
# 3. 404 on API calls → Verify backend URL is correct
```

### Backend Issues
```bash
# Check logs in hosting platform dashboard

# Common issues:
# 1. "GROQ_API_KEY not found" → Set environment variable
# 2. "Failed to connect to Qdrant" → Check QDRANT_URL and API key
# 3. CORS errors in frontend → Update CORS_ORIGINS to match frontend URL
```

### Health Check URLs
```bash
# Backend health
curl https://your-backend-url/health

# Frontend (should load UI)
curl https://your-frontend-url

# API connection from frontend
# Check Network tab in browser DevTools for /verify calls
```

---

## 🎯 PRODUCTION CHECKLIST

### Frontend
- [ ] `NEXT_PUBLIC_API_URL` points to production backend
- [ ] Build completes without errors (`pnpm build`)
- [ ] No hardcoded localhost URLs in code
- [ ] Browser console shows no errors

### Backend
- [ ] All environment variables set (GROQ, QDRANT, CORS)
- [ ] `CORS_ORIGINS` includes production frontend URL
- [ ] Health endpoint returns `{"status":"healthy"}`
- [ ] Log level set to `WARNING` or `ERROR`
- [ ] No secrets in code or logs

### Integration
- [ ] Frontend can call backend `/health` endpoint
- [ ] Claim verification works end-to-end
- [ ] No CORS errors in browser console
- [ ] Response times < 5 seconds for cache hits

---

## 🚨 COMMON ERRORS & SOLUTIONS

### "CORS policy blocked this request"
```bash
# Solution: Update backend CORS_ORIGINS
CORS_ORIGINS=https://your-frontend-url.vercel.app
```

### "Failed to fetch" in browser
```bash
# Solution: Check NEXT_PUBLIC_API_URL
# Must be accessible from browser (not internal URL)
NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app
```

### "GROQ_API_KEY not found"
```bash
# Solution: Set in backend hosting platform
# Railway: Variables tab → Add GROQ_API_KEY
```

### Backend returns 500 error
```bash
# Solution: Check backend logs
# Railway: Deployments → Click deployment → View logs
# Look for Python exceptions
```

---

## 📈 SCALING CONSIDERATIONS

### Frontend Scaling
- Vercel automatically scales to traffic
- No database, fully stateless
- CDN-cached static assets

### Backend Scaling
- Add more Railway instances for high traffic
- Consider rate limiting (already implemented)
- Monitor Groq API quota usage

### Cost Optimization
- Frontend: Free tier on Vercel (hobby plan)
- Backend: ~$5/month on Railway (starter plan)
- Qdrant: Free tier (1GB storage)
- Groq: Free tier (generous limits)

---

## 🔐 SECURITY BEST PRACTICES

1. **Never expose backend secrets to frontend**
   - Only use `NEXT_PUBLIC_*` for frontend vars
   - Keep API keys backend-only

2. **Use HTTPS in production**
   - Both platforms provide SSL certificates
   - Enforce HTTPS redirects

3. **Restrict CORS origins**
   - Don't use `allow_origins=["*"]`
   - Explicitly list frontend URLs

4. **Monitor API usage**
   - Set up alerts for quota limits
   - Log suspicious verification patterns

5. **Rate limiting**
   - Already implemented (100 requests/hour/IP)
   - Adjust in `api_server.py` if needed

---

## ✅ VERIFICATION CHECKLIST

- [ ] Frontend deploys successfully
- [ ] Backend deploys successfully
- [ ] Health endpoint responds
- [ ] Frontend can reach backend
- [ ] Claim verification works
- [ ] No CORS errors
- [ ] All environment variables set
- [ ] Logs show no errors
- [ ] Both services accessible via HTTPS

---

**Status: SPLIT DEPLOYMENT READY** ✅

Both frontend and backend can be deployed independently to different platforms and communicate via HTTP API with proper CORS configuration.
