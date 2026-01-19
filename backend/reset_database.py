"""Clear all old data and reingest with fresh timestamps"""
import sys
sys.path.insert(0, '.')

from src.agents.memory import MemoryUpdateAgent
from qdrant_client import QdrantClient
from src.config import QDRANT_URL, QDRANT_API_KEY, COLLECTION_NAME

print("Clearing old collection and recreating with fresh data...\n")

# Delete old collection
client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
try:
    client.delete_collection(COLLECTION_NAME)
    print(f"✓ Deleted old collection '{COLLECTION_NAME}'")
except:
    print(f"Collection '{COLLECTION_NAME}' didn't exist")

# Create new collection
memory_agent = MemoryUpdateAgent()
memory_agent.ensure_collection_exists()
print(f"✓ Created fresh collection\n")

# Run ingestion
print("Running data ingestion with fresh timestamps...")
from src.data_ingestion import ingest_all_datasets
result = ingest_all_datasets(use_real_datasets=True)

print("\n" + "="*60)
print("✅ DONE! All data now has fresh timestamps (< 7 days old)")
print("="*60)
