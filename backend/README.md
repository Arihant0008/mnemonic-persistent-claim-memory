# Mnemonic Backend

FastAPI REST API for claim verification with multi-agent pipeline.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Configure API keys (required)
# Edit .env and add:
# GROQ_API_KEY=your_key
# QDRANT_URL=your_url
# QDRANT_API_KEY=your_key
# CORS_ORIGINS=http://localhost:3000

# Run server
uvicorn api_server:app --reload --host 0.0.0.0 --port 8000
```

## 🌐 Deploy to Render

### Via Render Dashboard
1. Create new Web Service
2. Connect repository
3. Set **Root Directory** to `backend`
4. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn api_server:app --host 0.0.0.0 --port $PORT`
5. Add environment variables:
   - `GROQ_API_KEY`
   - `QDRANT_URL`
   - `QDRANT_API_KEY`
   - `CORS_ORIGINS` (your frontend URL)
   - `LOG_LEVEL=WARNING`
6. Deploy

### Environment Variables

```bash
# Required
GROQ_API_KEY=gsk_xxx
QDRANT_URL=https://xxx.cloud.qdrant.io
QDRANT_API_KEY=xxx
CORS_ORIGINS=https://your-frontend.vercel.app

# Optional
TAVILY_API_KEY=tvly_xxx
LOG_LEVEL=WARNING
```

## 🧪 Test Deployment

```bash
curl https://your-backend.onrender.com/health
```

Expected:
```json
{"status":"healthy","qdrant_connected":true,"tavily_available":true}
```

## 📚 Documentation

- [Main README](../README.md)
- [Split Deployment Guide](../SPLIT_DEPLOYMENT.md)
- [Architecture](../ARCHITECTURE.md)

## 🔧 Tech Stack

- FastAPI
- Python 3.10+
- Groq (Llama 3.1 8B)
- Qdrant Cloud
- Tavily API
