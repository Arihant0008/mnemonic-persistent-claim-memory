"""
Quick setup script for PCM system.
Validates configuration and ingests initial data.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))


def check_dependencies():
    """Check if required packages are installed."""
    required = [
        'qdrant_client',
        'fastembed',
        'groq',
        'streamlit',
        'langgraph'
    ]
    
    missing = []
    for pkg in required:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)
    
    if missing:
        print(f"❌ Missing packages: {', '.join(missing)}")
        print(f"   Run: pip install -r requirements.txt")
        return False
    
    print("✅ All required packages installed")
    return True


def check_config():
    """Validate configuration."""
    from src.config import validate_config, QDRANT_URL, GROQ_API_KEY
    
    try:
        validate_config()
        print("✅ Configuration validated")
        print(f"   Qdrant: {QDRANT_URL[:50]}...")
        print(f"   Groq: {GROQ_API_KEY[:20]}...")
        return True
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        return False


def check_qdrant_connection():
    """Test Qdrant connection."""
    from qdrant_client import QdrantClient
    from src.config import QDRANT_URL, QDRANT_API_KEY
    
    try:
        client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
        collections = client.get_collections()
        print(f"✅ Connected to Qdrant ({len(collections.collections)} collections)")
        return True
    except Exception as e:
        print(f"❌ Qdrant connection failed: {e}")
        return False


def setup_collection():
    """Ensure collection exists."""
    from src.agents.memory import MemoryUpdateAgent
    
    try:
        agent = MemoryUpdateAgent()
        agent.ensure_collection_exists()
        print("✅ Collection ready")
        return True
    except Exception as e:
        print(f"❌ Collection setup failed: {e}")
        return False


def ingest_data():
    """Ingest initial data."""
    from src.data_ingestion import ingest_all_datasets
    
    print("\n📊 Ingesting data...")
    try:
        result = ingest_all_datasets(use_real_datasets=True)
        print(f"✅ Ingested {result['success_count']} claims")
        return True
    except Exception as e:
        print(f"❌ Ingestion failed: {e}")
        return False


def main():
    print("=" * 50)
    print("🔍 PCM Setup Script")
    print("=" * 50)
    print()
    
    steps = [
        ("Checking dependencies", check_dependencies),
        ("Validating configuration", check_config),
        ("Testing Qdrant connection", check_qdrant_connection),
        ("Setting up collection", setup_collection),
        ("Ingesting initial data", ingest_data),
    ]
    
    for name, func in steps:
        print(f"\n🔄 {name}...")
        if not func():
            print(f"\n❌ Setup failed at: {name}")
            sys.exit(1)
    
    print("\n" + "=" * 50)
    print("✅ Setup complete!")
    print("=" * 50)
    print("\nNext steps:")
    print("  1. Run the app: streamlit run app.py")
    print("  2. Or use CLI: python cli.py verify 'Vaccines cause autism'")
    print()


if __name__ == "__main__":
    main()
