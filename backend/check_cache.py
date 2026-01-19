import sys
sys.path.insert(0, '.')
from src.agents.retriever import RetrievalAgent
from src.config import CACHE_HIT_THRESHOLD, CACHE_MAX_AGE_DAYS
from datetime import datetime

print("Checking cache for 'Vaccines cause autism'...\n")

r = RetrievalAgent()
results = r.search('Vaccines cause autism', k=3)

print(f"Found {len(results)} similar claims in memory\n")
print(f"Cache thresholds:")
print(f"  - Similarity: {CACHE_HIT_THRESHOLD}")
print(f"  - Max age: {CACHE_MAX_AGE_DAYS} days\n")
print("="*60)

for i, res in enumerate(results, 1):
    print(f"\n{i}. Claim: {res.claim_text}")
    print(f"   Similarity: {res.similarity_score:.3f} {'✓' if res.similarity_score >= CACHE_HIT_THRESHOLD else '✗'}")
    print(f"   Source: {res.source}")
    print(f"   Seen: {res.seen_count}x")
    print(f"   Timestamp: {res.timestamp}")
    
    # Check age
    try:
        cached_time = datetime.fromisoformat(res.timestamp.replace("Z", "+00:00"))
        age_days = (datetime.now(cached_time.tzinfo) - cached_time).days if cached_time.tzinfo else (datetime.now() - cached_time).days
        print(f"   Age: {age_days} days {'✓' if age_days <= CACHE_MAX_AGE_DAYS else '✗'}")
        
        if res.similarity_score >= CACHE_HIT_THRESHOLD and age_days <= CACHE_MAX_AGE_DAYS:
            print(f"   >>> CACHE HIT! <<<")
    except Exception as e:
        print(f"   Age check error: {e}")

print("\n" + "="*60)
