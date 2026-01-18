"""
FastAPI Backend for Mnemonic
Serves the verification API at localhost:8000
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
import sys
import os
import logging

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.pipeline import create_pipeline
from src.validation import validate_claim_input, ValidationError

# Configure logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "WARNING").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Mnemonic API", version="1.0.0")

# CORS middleware - environment-based configuration
ALLOWED_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in ALLOWED_ORIGINS],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)

# Rate limiting
try:
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.util import get_remote_address
    from slowapi.errors import RateLimitExceeded
    
    limiter = Limiter(key_func=get_remote_address, default_limits=["100/hour"])
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    logger.info("Rate limiting enabled")
except ImportError:
    limiter = None
    logger.warning("slowapi not installed - rate limiting disabled")

class ClaimRequest(BaseModel):
    raw_text: str = Field(..., min_length=3, max_length=2000, description="Claim text to verify")
    
    @field_validator('raw_text')
    @classmethod
    def validate_text(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Claim text cannot be empty")
        if not any(c.isalpha() for c in v):
            raise ValueError("Claim must contain text characters")
        return v.strip()

class VerificationResponse(BaseModel):
    normalized_claim: str | None = None
    cache_hit: bool = False
    verification_result: dict | None = None
    retrieved_evidence: list | None = None
    web_search_results: dict | None = None
    web_search_used: bool = False
    seen_count: int = 0
    timestamp: str

@app.get("/")
def root():
    return {"message": "Mnemonic API", "status": "online"}

@app.post("/verify")
async def verify_claim(request: ClaimRequest, req: Request):
    """Verify a claim through the multi-agent pipeline."""
    # Apply rate limiting if available
    if limiter:
        try:
            limiter.check_rate_limit(req)
        except:
            pass  # Rate limit handled by decorator
    
    try:
        # Additional sanitization at API boundary
        try:
            sanitized_text = validate_claim_input(request.raw_text)
        except ValidationError as e:
            logger.warning(f"Validation error: {e}")
            raise HTTPException(status_code=400, detail=str(e))
        
        logger.info("Processing verification request")
        
        # Create pipeline
        pipeline = create_pipeline()
        
        # Initial state
        initial_state = {
            "raw_text": sanitized_text,
            "image_path": None,
            "normalized_claim": None,
            "claim_embedding": None,
            "retrieved_evidence": None,
            "cache_hit": False,
            "web_search_results": None,
            "web_search_used": False,
            "verification_result": None,
            "memory_update_result": None,
            "timestamp": datetime.now().isoformat(),
            "errors": []
        }
        
        # Run pipeline
        result = pipeline.invoke(initial_state)
        
        logger.info("Pipeline completed successfully")
        
        # Extract seen count from memory update
        seen_count = 0
        if result.get("memory_update_result"):
            seen_count = result["memory_update_result"].get("seen_count", 0)
        
        # Handle errors in result
        if result.get("errors"):
            logger.warning(f"Pipeline errors: {result['errors']}")
        
        # Extract verification result and normalize fields
        verification_result = result.get("verification_result", {})
        if verification_result:
            # Map 'explanation' to 'reasoning' for frontend compatibility
            if 'explanation' in verification_result and 'reasoning' not in verification_result:
                verification_result['reasoning'] = verification_result['explanation']
        
        response = {
            "normalized_claim": result.get("normalized_claim"),
            "cache_hit": result.get("cache_hit", False),
            "verification_result": verification_result or {
                "verdict": "ERROR",
                "confidence": 0,
                "reasoning": f"Pipeline errors: {', '.join(result.get('errors', ['Unknown error']))}"
            },
            "retrieved_evidence": result.get("retrieved_evidence"),
            "web_search_results": result.get("web_search_results"),
            "web_search_used": result.get("web_search_used", False),
            "seen_count": seen_count,
            "timestamp": result.get("timestamp", datetime.now().isoformat())
        }
        
        return response
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        # Log full error internally
        logger.exception("Verification failed")
        # Return generic error to client
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting Mnemonic API Server...")
    logger.info("📡 Backend: http://localhost:8000")
    logger.info("🔍 Frontend: http://localhost:3000")
    logger.info("📚 Docs: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level=LOG_LEVEL.lower())
