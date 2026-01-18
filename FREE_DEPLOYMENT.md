# 🚀 FREE DEPLOYMENT GUIDE

## Overview

This repository is structured for **zero-cost deployment** using:
- **Frontend**: Vercel (Free tier)
- **Backend**: Render (Free tier)

Both services deploy from the same GitHub repository using subdirectories.

---

## 📦 Prerequisites

### API Keys (Free Tiers)
1. **Groq** - https://console.groq.com (Required)
2. **Qdrant Cloud** - https://cloud.qdrant.io (Required)
3. **Tavily** - https://tavily.com (Optional)

### Accounts
- GitHub account
- Vercel account (sign up with GitHub)
- Render account (sign up with GitHub)

---

## 🎯 STEP 1: Deploy Backend (Render)

### 1.1 Create Web Service
1. Go to https://render.com/dashboard
2. Click **New** → **Web Service**
3. Connect your GitHub repository

### 1.2 Configure Service
```
Name: mnemonic-backend
Region: Choose closest to you
Branch: main
Root Directory: backend
Runtime: Python 3
```

### 1.3 Build & Start Commands
```
Build Command: pip install -r requirements.txt
Start Command: uvicorn api_server:app --host 0.0.0.0 --port $PORT
```

### 1.4 Add Environment Variables
Click **Environment** → **Add Environment Variable**:

```bash
GROQ_API_KEY=gsk_your_actual_key_here
QDRANT_URL=https://your-cluster.cloud.qdrant.io
QDRANT_API_KEY=your_qdrant_key_here
CORS_ORIGINS=https://your-app.vercel.app
LOG_LEVEL=WARNING
```

> **Note**: You'll update `CORS_ORIGINS` after deploying the frontend

### 1.5 Deploy
1. Click **Create Web Service**
2. Wait for deployment (5-10 minutes first time)
3. Note your backend URL: `https://mnemonic-backend.onrender.com`

### 1.6 Verify Backend
```bash
curl https://your-backend.onrender.com/health
```

Expected response:
```json
{"status":"healthy","qdrant_connected":true,"tavily_available":true}
```

---

## 🎨 STEP 2: Deploy Frontend (Vercel)

### 2.1 Import Project
1. Go to https://vercel.com/new
2. Import your GitHub repository
3. Click **Import**

### 2.2 Configure Project
```
Framework Preset: Next.js
Root Directory: frontend
Build Command: (leave default)
Output Directory: (leave default)
Install Command: pnpm install
```

### 2.3 Add Environment Variable
Click **Environment Variables** → Add:

```
Key: NEXT_PUBLIC_API_URL
Value: https://your-backend.onrender.com
```

> Use your actual Render backend URL from Step 1.5

### 2.4 Deploy
1. Click **Deploy**
2. Wait for deployment (2-3 minutes)
3. Note your frontend URL: `https://your-app.vercel.app`

### 2.5 Test Frontend
Visit your Vercel URL and try verifying a claim.

---

## 🔗 STEP 3: Connect Frontend & Backend

### 3.1 Update Backend CORS
1. Go to Render dashboard
2. Select your backend service
3. Go to **Environment** tab
4. Update `CORS_ORIGINS`:
   ```
   CORS_ORIGINS=https://your-app.vercel.app
   ```
5. Click **Save Changes**
6. Backend will auto-redeploy

### 3.2 Verify Connection
1. Open your frontend URL
2. Open browser console (F12)
3. Submit a test claim
4. Check Network tab for successful API calls
5. No CORS errors should appear

---

## ✅ Verification Checklist

### Backend (Render)
- [ ] Service deploys successfully
- [ ] Health endpoint returns `{"status":"healthy"}`
- [ ] No errors in Render logs
- [ ] All environment variables set
- [ ] CORS_ORIGINS matches frontend URL

### Frontend (Vercel)
- [ ] Site loads without errors
- [ ] Can submit claims
- [ ] Gets responses from backend
- [ ] No CORS errors in console
- [ ] System status shows "Connected"

### Integration
- [ ] Claims verify successfully
- [ ] Evidence displays correctly
- [ ] Web search works (if Tavily key provided)
- [ ] Session history updates
- [ ] No 404 or 500 errors

---

## 🆓 Free Tier Limits

### Vercel Free Tier
- ✅ 100 GB bandwidth/month
- ✅ Unlimited deployments
- ✅ Custom domains
- ✅ Automatic HTTPS

### Render Free Tier
- ✅ 750 hours/month (always-on possible)
- ⚠️ Service sleeps after 15 min inactivity
- ⚠️ Cold start: 30-60 seconds
- ✅ Automatic HTTPS

### Groq Free Tier
- ✅ 30 requests/minute
- ✅ 14,400 requests/day
- ✅ No credit card required

### Qdrant Cloud Free Tier
- ✅ 1 GB storage
- ✅ Unlimited queries
- ✅ No credit card required

---

## 🐛 Common Issues

### Issue: "Service Unavailable" on first request
**Cause**: Render free tier sleeps after inactivity  
**Solution**: Wait 30-60 seconds for cold start, then retry

### Issue: CORS errors in browser
**Cause**: Backend CORS_ORIGINS doesn't match frontend URL  
**Solution**: Update CORS_ORIGINS in Render, ensure no trailing slash

### Issue: "GROQ_API_KEY not found"
**Cause**: Environment variable not set or typo  
**Solution**: Check Render environment tab, ensure exact spelling

### Issue: Frontend shows "API offline"
**Cause**: Backend URL incorrect or backend not running  
**Solution**: 
1. Check NEXT_PUBLIC_API_URL in Vercel
2. Visit backend /health endpoint directly
3. Check Render logs for errors

### Issue: Build fails on Vercel
**Cause**: Missing dependencies or wrong root directory  
**Solution**: 
1. Ensure Root Directory = `frontend`
2. Check frontend/package.json exists
3. Try manual redeploy

---

## 🔄 Updating Deployments

### Update Frontend
```bash
# Local: make changes in frontend/
git add frontend/
git commit -m "Update frontend"
git push

# Vercel auto-deploys on push
```

### Update Backend
```bash
# Local: make changes in backend/
git add backend/
git commit -m "Update backend"
git push

# Render auto-deploys on push
```

### Update Environment Variables
- **Vercel**: Settings → Environment Variables → Edit → Save → Redeploy
- **Render**: Environment tab → Edit → Save (auto-redeploys)

---

## 📊 Monitoring

### Vercel Analytics
- Dashboard shows request counts
- Check deployment logs
- View build logs

### Render Logs
- Dashboard → your service → Logs
- Real-time Python output
- Check for errors/warnings

### Health Checks
Set up a cron job or monitoring service (like UptimeRobot) to ping:
```
https://your-backend.onrender.com/health
```
This prevents cold starts and monitors uptime.

---

## 🎉 Success!

You now have:
- ✅ Frontend deployed to Vercel
- ✅ Backend deployed to Render
- ✅ Both communicating successfully
- ✅ Zero monthly cost
- ✅ Automatic HTTPS
- ✅ Continuous deployment from GitHub

**Share your deployment**: `https://your-app.vercel.app`

---

## 📚 Next Steps

- Add custom domain in Vercel
- Set up monitoring/alerts
- Review Render logs regularly
- Consider upgrading for production workloads
- Add analytics (Vercel Analytics, Google Analytics)

## 🆘 Support

- Vercel Docs: https://vercel.com/docs
- Render Docs: https://render.com/docs
- GitHub Issues: [Your repo]/issues
