"""
LangGraph Pipeline Orchestration with Web Search
Connects all agents into a coherent workflow for claim verification.
Includes intelligent caching: check memory first, then web search if needed.
"""

import logging
from typing import TypedDict, Optional
from datetime import datetime, timedelta

from langgraph.graph import StateGraph, END

logger = logging.getLogger(__name__)


class PipelineState(TypedDict):
    """State that flows through the pipeline."""
    # Input
    raw_text: Optional[str]
    image_path: Optional[str]
    
    # After normalization
    normalized_claim: Optional[dict]
    claim_embedding: Optional[list]
    
    # After memory retrieval
    retrieved_evidence: Optional[list]
    cache_hit: bool  # True if we found a good match in memory
    
    # After web search (only if cache miss)
    web_search_results: Optional[dict]
    web_search_used: bool
    
    # After reasoning
    verification_result: Optional[dict]
    
    # After memory update
    memory_update_result: Optional[dict]
    
    # Metadata
    timestamp: str
    errors: list


def create_pipeline():
    """
    Create the multi-agent pipeline using LangGraph.
    
    Pipeline flow:
    1. Normalizer: Extract and normalize claim from input
    2. Memory Retriever: Check if claim exists in memory (cache)
    3. Web Search: If cache miss, search the internet
    4. Reasoner: Analyze claim with all evidence
    5. Memory Update: Store result for future lookups
    """
    from src.agents.normalizer import ClaimNormalizer
    from src.agents.retriever import RetrievalAgent
    from src.agents.reasoner import ReasoningAgent
    from src.agents.memory import MemoryUpdateAgent
    from src.config import CACHE_HIT_THRESHOLD, CACHE_MAX_AGE_DAYS
    
    # Initialize agents
    normalizer = ClaimNormalizer()
    retriever = RetrievalAgent()
    reasoner = ReasoningAgent()
    memory_agent = MemoryUpdateAgent()
    
    # Try to initialize web search agent
    web_search_agent = None
    try:
        from src.agents.web_search import WebSearchAgent
        web_search_agent = WebSearchAgent()
        logger.info("Web search enabled (Tavily)")
    except Exception as e:
        logger.warning(f"Web search disabled: {e}")
    
    def normalize_node(state: PipelineState) -> PipelineState:
        """Normalize the input claim."""
        try:
            result = normalizer.process(
                text=state.get("raw_text"),
                image_path=state.get("image_path")
            )
            
            embedding = retriever._get_embedding(result.normalized_text)
            
            state["normalized_claim"] = normalizer.to_dict(result)
            state["claim_embedding"] = embedding
            
        except Exception as e:
            state["errors"].append(f"Normalization error: {str(e)}")
            state["normalized_claim"] = {
                "original_text": state.get("raw_text", ""),
                "normalized_text": state.get("raw_text", ""),
                "entities": [],
                "temporal_markers": None,
                "source_type": "text"
            }
        
        return state
    
    def retrieve_node(state: PipelineState) -> PipelineState:
        """Check memory for similar claims (cache check)."""
        try:
            normalized_text = state["normalized_claim"]["normalized_text"]
            
            # Search for similar claims
            results = retriever.search(normalized_text, k=10)
            
            # Convert to serializable format
            state["retrieved_evidence"] = [
                {
                    "id": r.id,
                    "claim_text": r.claim_text,
                    "verdict": r.verdict,
                    "confidence": r.confidence,
                    "source": r.source,
                    "source_reliability": r.source_reliability,
                    "similarity_score": r.similarity_score,
                    "time_decayed_score": r.time_decayed_score,
                    "seen_count": r.seen_count,
                    "timestamp": r.timestamp
                }
                for r in results
            ]
            
            # Check if we have a cache hit
            if results:
                best_match = results[0]
                is_recent = True
                
                # Check age of the cached result
                if best_match.timestamp:
                    try:
                        cached_time = datetime.fromisoformat(best_match.timestamp.replace("Z", "+00:00"))
                        age_days = (datetime.now(cached_time.tzinfo) - cached_time).days if cached_time.tzinfo else (datetime.now() - cached_time).days
                        is_recent = age_days <= CACHE_MAX_AGE_DAYS
                    except:
                        is_recent = True
                
                # Cache hit if high similarity AND recent
                state["cache_hit"] = (
                    best_match.similarity_score >= CACHE_HIT_THRESHOLD 
                    and is_recent
                )
            else:
                state["cache_hit"] = False
            
        except Exception as e:
            state["errors"].append(f"Retrieval error: {str(e)}")
            state["retrieved_evidence"] = []
            state["cache_hit"] = False
        
        return state
    
    def web_search_node(state: PipelineState) -> PipelineState:
        """Search the web if cache miss."""
        state["web_search_used"] = False
        state["web_search_results"] = None
        
        # Skip web search if cache hit
        if state.get("cache_hit", False):
            return state
        
        # Skip if no web search agent
        if web_search_agent is None:
            return state
        
        try:
            normalized_text = state["normalized_claim"]["normalized_text"]
            
            # Perform web search
            response = web_search_agent.search_for_fact_check(normalized_text)
            
            if response.results:
                state["web_search_used"] = True
                state["web_search_results"] = {
                    "query": response.query,
                    "answer": response.answer,
                    "search_time": response.search_time,
                    "sources": [
                        {
                            "title": r.title,
                            "url": r.url,
                            "content": r.content[:500],
                            "score": r.score
                        }
                        for r in response.results
                    ]
                }
            
        except Exception as e:
            state["errors"].append(f"Web search error: {str(e)}")
        
        return state
    
    def reason_node(state: PipelineState) -> PipelineState:
        """Reason about the claim using all available evidence."""
        try:
            from src.agents.retriever import RetrievedClaim
            
            # Build evidence from memory
            memory_evidence = []
            for ev in state.get("retrieved_evidence", []):
                memory_evidence.append(
                    RetrievedClaim(
                        id=ev["id"],
                        claim_text=ev["claim_text"],
                        normalized_text=ev.get("claim_text", ""),
                        verdict=ev["verdict"],
                        confidence=ev["confidence"],
                        source=ev["source"],
                        source_reliability=ev["source_reliability"],
                        timestamp=ev.get("timestamp", ""),
                        seen_count=ev["seen_count"],
                        similarity_score=ev["similarity_score"],
                        time_decayed_score=ev["time_decayed_score"]
                    )
                )
            
            # If we have web search results, incorporate them into reasoning
            web_context = ""
            if state.get("web_search_used") and state.get("web_search_results"):
                web = state["web_search_results"]
                web_context = f"\n\nWEB SEARCH RESULTS ({len(web['sources'])} sources found):\n"
                
                if web.get("answer"):
                    web_context += f"Direct Answer: {web['answer']}\n\n"
                
                for i, src in enumerate(web["sources"][:5], 1):
                    web_context += f"{i}. {src['title']}\n"
                    web_context += f"   URL: {src['url']}\n"
                    web_context += f"   Content: {src['content'][:300]}...\n\n"
            
            # Enhanced reasoning with web search
            result = reasoner.reason(
                claim_text=state["normalized_claim"]["original_text"],
                normalized_claim=state["normalized_claim"]["normalized_text"],
                evidence=memory_evidence,
                web_context=web_context if web_context else None
            )
            
            state["verification_result"] = {
                "claim_text": result.claim_text,
                "normalized_claim": result.normalized_claim,
                "verdict": result.verdict,
                "confidence": result.confidence,
                "explanation": result.explanation,
                "evidence_ids": result.evidence_ids,
                "evidence_summary": result.evidence_summary,
                "reasoning_trace": result.reasoning_trace,
                "web_search_used": state.get("web_search_used", False)
            }
            
        except Exception as e:
            state["errors"].append(f"Reasoning error: {str(e)}")
            state["verification_result"] = {
                "claim_text": state["normalized_claim"]["original_text"],
                "normalized_claim": state["normalized_claim"]["normalized_text"],
                "verdict": "Uncertain",
                "confidence": 0.3,
                "explanation": f"Error during reasoning: {str(e)}",
                "evidence_ids": [],
                "evidence_summary": "Error occurred",
                "reasoning_trace": "",
                "web_search_used": False
            }
        
        return state
    
    def memory_node(state: PipelineState) -> PipelineState:
        """Update memory with verification result."""
        try:
            from src.agents.reasoner import VerificationResult
            
            vr = state["verification_result"]
            verification = VerificationResult(
                claim_text=vr["claim_text"],
                normalized_claim=vr["normalized_claim"],
                verdict=vr["verdict"],
                confidence=vr["confidence"],
                explanation=vr["explanation"],
                evidence_ids=vr["evidence_ids"],
                evidence_summary=vr["evidence_summary"],
                reasoning_trace=vr["reasoning_trace"]
            )
            
            result = memory_agent.update_or_create(verification)
            
            state["memory_update_result"] = {
                "action": result.action,
                "claim_id": result.claim_id,
                "seen_count": result.seen_count,
                "message": result.message
            }
            
        except Exception as e:
            state["errors"].append(f"Memory update error: {str(e)}")
            state["memory_update_result"] = {
                "action": "error",
                "claim_id": "",
                "seen_count": 0,
                "message": str(e)
            }
        
        return state
    
    # Build the graph
    workflow = StateGraph(PipelineState)
    
    # Add nodes
    workflow.add_node("normalizer", normalize_node)
    workflow.add_node("retriever", retrieve_node)
    workflow.add_node("web_search", web_search_node)
    workflow.add_node("reasoner", reason_node)
    workflow.add_node("memory", memory_node)
    
    # Define edges (linear flow with web search)
    workflow.set_entry_point("normalizer")
    workflow.add_edge("normalizer", "retriever")
    workflow.add_edge("retriever", "web_search")
    workflow.add_edge("web_search", "reasoner")
    workflow.add_edge("reasoner", "memory")
    workflow.add_edge("memory", END)
    
    return workflow.compile()


class ClaimVerificationPipeline:
    """
    High-level interface for claim verification.
    Wraps the LangGraph pipeline with a clean API.
    """
    
    def __init__(self):
        self.pipeline = create_pipeline()
    
    def verify(
        self,
        text: Optional[str] = None,
        image_path: Optional[str] = None
    ) -> dict:
        """
        Verify a claim.
        
        Args:
            text: Text claim to verify
            image_path: Path to image containing claim
            
        Returns:
            Dictionary with verification results
            
        Raises:
            ValueError: If input is invalid
        """
        if not text and not image_path:
            raise ValueError("Either text or image_path must be provided")
        
        # SECURITY: Validate input length to prevent abuse
        MAX_CLAIM_LENGTH = 2000
        if text and len(text) > MAX_CLAIM_LENGTH:
            raise ValueError(f"Claim text exceeds maximum length of {MAX_CLAIM_LENGTH} characters")
        
        initial_state: PipelineState = {
            "raw_text": text,
            "image_path": image_path,
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
        
        # Run the pipeline
        final_state = self.pipeline.invoke(initial_state)
        
        return {
            "input": {
                "text": text,
                "image_path": image_path
            },
            "normalized_claim": final_state.get("normalized_claim"),
            "cache_hit": final_state.get("cache_hit", False),
            "web_search_used": final_state.get("web_search_used", False),
            "web_search_results": final_state.get("web_search_results"),
            "evidence": final_state.get("retrieved_evidence", [])[:5],
            "verification": final_state.get("verification_result"),
            "memory": final_state.get("memory_update_result"),
            "errors": final_state.get("errors", []),
            "timestamp": final_state.get("timestamp")
        }
    
    def verify_batch(self, claims: list[str]) -> list[dict]:
        """Verify multiple claims."""
        results = []
        for claim in claims:
            try:
                result = self.verify(text=claim)
                results.append(result)
            except Exception as e:
                results.append({
                    "input": {"text": claim},
                    "error": str(e)
                })
        return results


if __name__ == "__main__":
    # Test the pipeline
    pipeline = ClaimVerificationPipeline()
    
    test_claims = [
        "Vaccines cause autism in children",
        "Donald Trump is the current US president",
        "The Earth is flat"
    ]
    
    for claim in test_claims:
        print(f"\n{'='*60}")
        print(f"Testing: {claim}")
        print("="*60)
        
        result = pipeline.verify(text=claim)
        
        print(f"Cache hit: {result.get('cache_hit', False)}")
        print(f"Web search used: {result.get('web_search_used', False)}")
        
        if result.get("verification"):
            v = result["verification"]
            print(f"Verdict: {v['verdict']}")
            print(f"Confidence: {v['confidence']:.0%}")
            print(f"Explanation: {v['explanation'][:200]}...")
        
        if result.get("memory"):
            m = result["memory"]
            print(f"Memory: {m['action']} - {m['message']}")
        
        if result.get("errors"):
            print(f"Errors: {result['errors']}")
