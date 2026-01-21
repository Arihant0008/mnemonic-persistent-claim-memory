"""
Test Memory Management Improvements
Validates that embedding models are properly cached and reused.
"""

import sys
sys.path.insert(0, '.')

def test_singleton_embedding_model():
    """Test that embedding model is a singleton."""
    from src.agents.memory import get_shared_embedding_model
    
    print("Testing singleton embedding model...")
    
    # Get model twice
    model1 = get_shared_embedding_model()
    model2 = get_shared_embedding_model()
    
    # Should be the same instance
    assert model1 is model2, "Models are not the same instance!"
    print("✓ Embedding model is properly cached (singleton)")
    
    return model1


def test_agent_cache():
    """Test that agents reuse the same embedding model."""
    from src.agents.memory import MemoryUpdateAgent
    from src.agents.retriever import RetrievalAgent
    
    print("\nTesting agent embedding model reuse...")
    
    # Create agents
    memory1 = MemoryUpdateAgent()
    retriever1 = RetrievalAgent()
    
    # Create again
    memory2 = MemoryUpdateAgent()
    retriever2 = RetrievalAgent()
    
    # All should use the same embedding model
    assert memory1.embed_model is memory2.embed_model, "Memory agents have different models!"
    assert retriever1.embed_model is retriever2.embed_model, "Retriever agents have different models!"
    assert memory1.embed_model is retriever1.embed_model, "Memory and Retriever use different models!"
    
    print("✓ All agents share the same embedding model")
    

def test_pipeline_cache():
    """Test that pipeline caches agents."""
    from src.pipeline import create_pipeline, _agent_cache
    
    print("\nTesting pipeline agent caching...")
    
    # Clear cache to start fresh
    _agent_cache.clear()
    
    # Create pipeline twice
    pipeline1 = create_pipeline()
    initial_cache_keys = set(_agent_cache.keys())
    
    pipeline2 = create_pipeline()
    second_cache_keys = set(_agent_cache.keys())
    
    # Cache should be populated
    assert len(_agent_cache) > 0, "Agent cache is empty!"
    print(f"✓ Agent cache populated with: {list(_agent_cache.keys())}")
    
    # Cache should be the same after second call
    assert initial_cache_keys == second_cache_keys, "Cache changed between calls!"
    print("✓ Pipeline reuses cached agents")


def test_memory_monitoring():
    """Test memory monitoring utilities."""
    from src.memory_monitor import (
        get_memory_usage, 
        log_memory_usage, 
        cleanup_memory,
        check_memory_limit
    )
    
    print("\nTesting memory monitoring...")
    
    # Get memory usage
    usage = get_memory_usage()
    assert 'rss_mb' in usage, "Missing RSS in memory usage"
    assert 'percent' in usage, "Missing percent in memory usage"
    print(f"✓ Current memory: {usage['rss_mb']:.1f}MB ({usage['percent']:.1f}%)")
    
    # Test logging
    log_usage = log_memory_usage("test")
    assert log_usage == usage, "Log memory usage mismatch"
    print("✓ Memory logging works")
    
    # Test cleanup
    freed = cleanup_memory()
    print(f"✓ Cleanup freed {freed:.1f}MB")
    
    # Test limit check
    under_limit = check_memory_limit(max_mb=10000)  # High limit for test
    assert under_limit, "Memory limit check failed"
    print("✓ Memory limit checking works")


if __name__ == "__main__":
    print("="*60)
    print("Memory Management Validation Tests")
    print("="*60)
    
    try:
        # Test 1: Singleton model
        model = test_singleton_embedding_model()
        
        # Test 2: Agent reuse
        test_agent_cache()
        
        # Test 3: Pipeline caching
        test_pipeline_cache()
        
        # Test 4: Memory monitoring
        test_memory_monitoring()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED")
        print("="*60)
        print("\nMemory optimizations are working correctly!")
        print("Ready to deploy to Render.")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
