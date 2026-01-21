# Memory Optimization Guide

## Problem Summary
Your Render service exceeded its 512MB memory limit, causing automatic restarts. This was caused by:

1. **Memory Leak**: Multiple embedding model instances were created on each request
2. **No Model Reuse**: FastEmbed models (~200-300MB each) weren't being cached
3. **Agent Recreation**: New agent instances on every API call

## Fixes Implemented

### 1. Singleton Embedding Model Pattern
- **File**: `backend/src/agents/memory.py`, `backend/src/agents/retriever.py`
- **Change**: Created `get_shared_embedding_model()` to ensure only ONE embedding model instance exists
- **Impact**: Reduces memory from ~200-300MB per request to a constant 200-300MB total

```python
# Before: Each agent created its own model
self.embed_model = TextEmbedding(TEXT_EMBEDDING_MODEL)  # 200-300MB each time!

# After: All agents share one model
self.embed_model = get_shared_embedding_model()  # Reuses single instance
```

### 2. Agent Instance Caching
- **File**: `backend/src/pipeline.py`
- **Change**: Cache all agents (`_agent_cache`) instead of recreating on each request
- **Impact**: Prevents memory accumulation from repeated agent initialization

```python
# Before: New agents every request
def create_pipeline():
    retriever = RetrievalAgent()  # New instance!
    memory_agent = MemoryUpdateAgent()  # New instance!

# After: Cached agents
if not _agent_cache:
    _agent_cache['retriever'] = RetrievalAgent()  # Once only
    _agent_cache['memory_agent'] = MemoryUpdateAgent()  # Once only
```

### 3. Memory Monitoring & Cleanup
- **File**: `backend/src/memory_monitor.py` (new)
- **Change**: Added monitoring, logging, and periodic garbage collection
- **Impact**: Proactive memory management and visibility

Features:
- `get_memory_usage()`: Track RSS, VMS, and available memory
- `cleanup_memory()`: Force garbage collection
- `check_memory_limit()`: Alert when approaching 512MB limit
- `log_memory_usage()`: Log memory stats with context

### 4. API Server Integration
- **File**: `backend/api_server.py`
- **Changes**:
  - Periodic GC every 10 requests
  - Memory limit checks before processing
  - Health endpoint with memory stats
  - Startup/shutdown memory logging

```python
# New health endpoint
GET /health
{
  "status": "healthy",
  "memory_mb": 245.3,
  "memory_percent": 47.9,
  "memory_limit_mb": 512
}
```

## Configuration

### Environment Variables
Add to your Render environment variables:

```bash
# Memory limit (MB) - Render free tier
MEMORY_LIMIT_MB=512

# Log level for debugging
LOG_LEVEL=INFO
```

### Render Service Settings
1. **Instance Type**: Free tier (512MB RAM)
2. **Auto-Deploy**: Enabled (for these fixes)
3. **Health Check Path**: `/health` (recommended)

## Monitoring

### Check Memory Usage
```bash
# Via health endpoint
curl https://your-service.onrender.com/health

# In logs, search for:
# - "Memory [startup]"
# - "Memory [after request #XX]"
# - "Periodic cleanup at request #XX"
# - "Memory limit exceeded"
```

### Log Interpretation
```
INFO - Memory [startup]: RSS=234.5MB, VMS=512.1MB, Usage=45.8%, Available=1234.5MB
```
- **RSS** (Resident Set Size): Actual RAM used - this is what Render counts
- **VMS** (Virtual Memory Size): Can be higher, includes swapped memory
- **Usage**: Percentage of system memory
- **Available**: Free system memory

## Expected Behavior After Fixes

### Memory Profile
- **Startup**: ~200-300MB (embedding model + agents)
- **Per Request**: +5-20MB (temporary state/embeddings)
- **After GC**: Returns to baseline (~200-300MB)
- **Maximum**: Should never exceed 450MB

### Before vs After
```
BEFORE (memory leak):
Request 1:  250MB
Request 10: 450MB (!)
Request 20: 600MB (CRASH!)

AFTER (optimized):
Request 1:  250MB
Request 10: 270MB (periodic GC)
Request 20: 265MB (stable)
Request 100: 280MB (still healthy)
```

## Additional Optimizations (If Needed)

If you still experience issues, consider:

### 1. Reduce Batch Sizes
In `backend/src/config.py`:
```python
DEFAULT_TOP_K = 5  # Reduced from 10
```

### 2. Upgrade Render Plan
- **Starter ($7/mo)**: 512MB → No change
- **Standard ($25/mo)**: 2GB RAM → Much more headroom

### 3. Use Lightweight Embedding Model
In `backend/src/config.py`:
```python
# Current: all-MiniLM-L6-v2 (384 dim, ~200MB)
TEXT_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Alternative: paraphrase-MiniLM-L3-v2 (384 dim, ~60MB)
TEXT_EMBEDDING_MODEL = "sentence-transformers/paraphrase-MiniLM-L3-v2"
```

### 4. Enable Model Quantization
In `backend/src/agents/memory.py`:
```python
def get_shared_embedding_model():
    if _embedding_model_cache is None:
        _embedding_model_cache = TextEmbedding(
            TEXT_EMBEDDING_MODEL,
            # Add quantization for smaller memory footprint
            model_kwargs={"torch_dtype": "float16"}
        )
    return _embedding_model_cache
```

## Testing Locally

### Install psutil
```bash
cd backend
pip install psutil
```

### Run with Memory Monitoring
```bash
# Start server
python api_server.py

# In another terminal, make requests and watch logs
curl -X POST http://localhost:8000/verify \
  -H "Content-Type: application/json" \
  -d '{"raw_text": "Test claim"}'

# Check health
curl http://localhost:8000/health
```

### Memory Test Script
Run `test_memory.py` to simulate load:
```bash
python backend/test_memory.py
```

## Deployment Checklist

- [x] Singleton embedding model implemented
- [x] Agent caching implemented
- [x] Memory monitoring added
- [x] Health endpoint with memory stats
- [x] Periodic garbage collection
- [x] psutil dependency added
- [ ] Test locally with memory monitoring
- [ ] Deploy to Render
- [ ] Monitor logs for memory metrics
- [ ] Check `/health` endpoint after deployment
- [ ] Verify no more memory crashes

## Troubleshooting

### Issue: Still seeing high memory
**Solution**: Check logs for which component uses memory:
```bash
# Render logs → search for "Memory"
# Look for RSS values > 400MB
```

### Issue: Slow response times after GC
**Solution**: Increase cleanup interval:
```python
# In api_server.py
_cleanup_interval = 20  # Was 10
```

### Issue: Model initialization fails
**Solution**: Check embedding model download:
```bash
# The model is cached in ~/.cache/fastembed/
# Render may need to download it on first start
# This is normal and only happens once
```

## Support
If issues persist after these fixes:
1. Check Render logs for memory patterns
2. Share `/health` endpoint output
3. Review memory logs around crash time
4. Consider upgrading instance type

---
**Last Updated**: January 21, 2026
**Changes By**: Memory leak fixes for Render deployment
