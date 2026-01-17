"""
Test suite for PCM system.
Run with: pytest tests/
"""

import pytest
import sys
import os

# Add parent to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestConfig:
    """Test configuration module."""
    
    def test_config_loads(self):
        """Test that config loads without errors."""
        from src.config import COLLECTION_NAME, TEXT_EMBEDDING_DIM
        
        assert COLLECTION_NAME == "claims_memory"
        assert TEXT_EMBEDDING_DIM == 384
    
    def test_validate_config(self):
        """Test config validation."""
        from src.config import validate_config
        
        # Should raise if env vars not set
        try:
            validate_config()
        except ValueError:
            pass  # Expected if env not configured


class TestNormalizer:
    """Test claim normalizer agent."""
    
    def test_normalizer_creates(self):
        """Test normalizer instantiation."""
        from src.agents.normalizer import ClaimNormalizer
        
        normalizer = ClaimNormalizer()
        assert normalizer is not None
    
    def test_normalize_simple_claim(self):
        """Test normalizing a simple claim."""
        from src.agents.normalizer import ClaimNormalizer
        
        normalizer = ClaimNormalizer()
        result = normalizer.normalize_text("Vaccines cause autism")
        
        assert result.original_text == "Vaccines cause autism"
        assert len(result.normalized_text) > 0


class TestRetriever:
    """Test retrieval agent."""
    
    def test_retriever_creates(self):
        """Test retriever instantiation."""
        from src.agents.retriever import RetrievalAgent
        
        retriever = RetrievalAgent()
        assert retriever is not None
    
    def test_embedding_generation(self):
        """Test embedding generation."""
        from src.agents.retriever import RetrievalAgent
        
        retriever = RetrievalAgent()
        embedding = retriever._get_embedding("Test claim")
        
        assert len(embedding) == 384  # Expected dimension


class TestReasoner:
    """Test reasoning agent."""
    
    def test_reasoner_creates(self):
        """Test reasoner instantiation."""
        from src.agents.reasoner import ReasoningAgent
        
        reasoner = ReasoningAgent()
        assert reasoner is not None


class TestMemory:
    """Test memory agent."""
    
    def test_memory_creates(self):
        """Test memory agent instantiation."""
        from src.agents.memory import MemoryUpdateAgent
        
        memory = MemoryUpdateAgent()
        assert memory is not None


class TestPipeline:
    """Test the full pipeline."""
    
    def test_pipeline_creates(self):
        """Test pipeline instantiation."""
        from src.pipeline import ClaimVerificationPipeline
        
        pipeline = ClaimVerificationPipeline()
        assert pipeline is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
