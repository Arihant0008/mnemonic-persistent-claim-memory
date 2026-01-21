# Quick Deployment Guide - Memory Fix

## What Was Fixed
Your service crashed because it created multiple copies of the embedding model (200-300MB each) on every request. We've implemented:

1. **Singleton embedding model** - Only ONE model instance ever exists
2. **Agent caching** - Agents are created once and reused
3. **Memory monitoring** - Tracks usage and runs cleanup automatically
4. **Health endpoint** - `/health` shows memory stats

## Deploy to Render

### Step 1: Commit and Push Changes
```bash
cd "c:\Users\Lenovo\OneDrive\Desktop\pmc opus anti"

# Add all changes
git add backend/

# Commit
git commit -m "Fix memory leak: singleton embeddings + agent caching"

# Push to trigger auto-deploy
git push origin main
```

### Step 2: Monitor Deployment
1. Go to Render dashboard: https://dashboard.render.com
2. Find your service: "Claim-Memory-Engine-for-Repeated-Content-Detection"
3. Watch the "Logs" tab during deployment
4. Look for these success messages:
   ```
   Initializing agent cache...
   Initializing shared embedding model: sentence-transformers/all-MiniLM-L6-v2
   Memory [startup]: RSS=XXX.XMB
   ```

### Step 3: Verify Fix
After deployment completes:

```bash
# Check health endpoint
curl https://your-service.onrender.com/health

# Expected response:
{
  "status": "healthy",
  "memory_mb": 234.5,
  "memory_percent": 45.8,
  "memory_limit_mb": 512
}
```

### Step 4: Test Under Load
Send a few test requests:
```bash
curl -X POST https://your-service.onrender.com/verify \
  -H "Content-Type: application/json" \
  -d '{"raw_text": "Vaccines cause autism"}'
```

Then check health again - memory should be stable (not increasing).

## Expected Memory Behavior

### Before Fix (BAD)
```
Startup:    200MB
Request 1:  250MB
Request 5:  350MB
Request 10: 450MB
Request 15: 550MB (CRASH!)
```

### After Fix (GOOD)
```
Startup:    220MB
Request 1:  235MB
Request 10: 245MB (cleanup)
Request 50: 250MB (stable!)
Request 100: 255MB (still healthy)
```

## Monitor in Render Logs

Search for these log patterns:

### Good Signs ✅
```
INFO - Initializing agent cache...
INFO - Memory [startup]: RSS=234.5MB
INFO - Periodic cleanup at request #10
INFO - GC collected 125 objects, freed 3.2MB
```

### Warning Signs ⚠️
```
WARNING - Memory usage (410.0MB) exceeds threshold
INFO - Running cleanup...
```

### Bad Signs (shouldn't happen now) ❌
```
ERROR - Memory limit exceeded: 520.0MB > 512MB
```

## Environment Variables (Optional)

Add these in Render Dashboard → Environment:

```bash
# Adjust memory limit if needed (default: 512)
MEMORY_LIMIT_MB=512

# Enable debug logging to see memory stats
LOG_LEVEL=INFO

# Adjust cleanup frequency (default: every 10 requests)
# Not exposed yet, but can be added if needed
```

## If Problems Persist

1. **Check the logs** in Render dashboard
2. **Look for memory patterns** - search for "Memory" or "RSS"
3. **Check health endpoint** - is memory still climbing?
4. **Share the logs** showing the crash
5. **Consider upgrading** to Standard tier (2GB RAM) for $25/mo

## Files Changed
- ✅ `backend/src/agents/memory.py` - Singleton embedding model
- ✅ `backend/src/agents/retriever.py` - Use shared model
- ✅ `backend/src/pipeline.py` - Agent caching
- ✅ `backend/src/memory_monitor.py` - New monitoring utilities
- ✅ `backend/api_server.py` - Memory monitoring integration
- ✅ `backend/requirements.txt` - Added psutil
- ✅ `MEMORY_FIX_GUIDE.md` - Detailed documentation

## Testing Locally First (Recommended)

```bash
cd backend

# Install psutil
pip install psutil

# Run validation tests
python test_memory_optimization.py

# Start server and watch memory
python api_server.py

# In another terminal, make some requests
curl -X POST http://localhost:8000/verify \
  -H "Content-Type: application/json" \
  -d '{"raw_text": "Test claim 1"}'

# Check health
curl http://localhost:8000/health
```

## Success Criteria
- ✅ Service stays up after 20+ requests
- ✅ Memory stays under 400MB
- ✅ `/health` shows stable memory_mb
- ✅ No more memory limit exceeded emails

## Need Help?
Check `MEMORY_FIX_GUIDE.md` for detailed explanations and troubleshooting.
