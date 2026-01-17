"""
Persistent Claim Memory - Streamlit Dashboard
Main application entry point for the misinformation detection system.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import time
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.config import validate_config, COLLECTION_NAME
from src.pipeline import ClaimVerificationPipeline
from src.agents.memory import MemoryUpdateAgent
from src.agents.retriever import RetrievalAgent

# Page configuration
st.set_page_config(
    page_title="Persistent Claim Memory",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for enhanced styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #6b7280;
        text-align: center;
        margin-bottom: 2rem;
    }
    .verdict-true {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 1rem 2rem;
        border-radius: 12px;
        font-size: 1.5rem;
        font-weight: 600;
        text-align: center;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
    }
    .verdict-false {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
        padding: 1rem 2rem;
        border-radius: 12px;
        font-size: 1.5rem;
        font-weight: 600;
        text-align: center;
        box-shadow: 0 4px 15px rgba(239, 68, 68, 0.3);
    }
    .verdict-uncertain {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white;
        padding: 1rem 2rem;
        border-radius: 12px;
        font-size: 1.5rem;
        font-weight: 600;
        text-align: center;
        box-shadow: 0 4px 15px rgba(245, 158, 11, 0.3);
    }
    .evidence-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .stat-card {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
    }
    .stat-value {
        font-size: 2rem;
        font-weight: 700;
    }
    .stat-label {
        font-size: 0.9rem;
        opacity: 0.8;
    }
    .memory-update {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables."""
    if 'pipeline' not in st.session_state:
        st.session_state.pipeline = None
    if 'memory_agent' not in st.session_state:
        st.session_state.memory_agent = None
    if 'last_result' not in st.session_state:
        st.session_state.last_result = None
    if 'verification_history' not in st.session_state:
        st.session_state.verification_history = []
    # Latency and cache tracking for live dashboard
    if 'total_queries' not in st.session_state:
        st.session_state.total_queries = 0
    if 'cache_hits' not in st.session_state:
        st.session_state.cache_hits = 0
    if 'web_searches' not in st.session_state:
        st.session_state.web_searches = 0
    if 'cache_latencies' not in st.session_state:
        st.session_state.cache_latencies = []
    if 'web_latencies' not in st.session_state:
        st.session_state.web_latencies = []


def render_memory_dashboard(retriever):
    """
    Render live memory statistics dashboard.
    This proves to judges that memory actually evolves over time.
    """
    try:
        stats = retriever.get_detailed_stats()
    except:
        stats = retriever.get_collection_stats()
    
    st.markdown("### 📊 Live Memory Dashboard")
    
    # Main stats row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{stats.get('total_claims', 0):,}</div>
            <div class="stat-label">📚 Total Claims in Memory</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Cache hit rate this session
        total = st.session_state.total_queries
        hits = st.session_state.cache_hits
        rate = (hits / total * 100) if total > 0 else 0
        
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{rate:.0f}%</div>
            <div class="stat-label">💾 Cache Hit Rate ({hits}/{total})</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        # Average latency comparison
        cache_avg = sum(st.session_state.cache_latencies) / len(st.session_state.cache_latencies) if st.session_state.cache_latencies else 0
        web_avg = sum(st.session_state.web_latencies) / len(st.session_state.web_latencies) if st.session_state.web_latencies else 0
        
        if cache_avg > 0 and web_avg > 0:
            speedup = web_avg / cache_avg
            latency_text = f"{speedup:.1f}x faster"
        elif cache_avg > 0:
            latency_text = f"{cache_avg:.1f}s avg"
        else:
            latency_text = "--"
        
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{latency_text}</div>
            <div class="stat-label">⚡ Cache vs Web Speed</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        # Memory evolution indicator
        avg_seen = stats.get('avg_seen_count', 0)
        max_seen = stats.get('max_seen_count', 0)
        
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{avg_seen:.1f}</div>
            <div class="stat-label">👁️ Avg Seen Count (max: {max_seen})</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Expandable section for detailed stats
    with st.expander("📈 Detailed Memory Stats"):
        subcol1, subcol2 = st.columns(2)
        
        with subcol1:
            # Verdict breakdown
            verdicts = stats.get('verdicts', {})
            st.markdown("**Verdict Breakdown:**")
            if verdicts:
                for verdict, count in verdicts.items():
                    emoji = {"True": "✅", "False": "❌", "Uncertain": "❓"}.get(verdict, "")
                    st.write(f"{emoji} {verdict}: {count}")
            
            # Claims in last 24h
            st.write(f"📅 Claims added (24h): {stats.get('claims_last_24h', 0)}")
        
        with subcol2:
            # Top claims by seen_count
            st.markdown("**Most Verified Claims:**")
            top_claims = stats.get('top_claims', [])
            if top_claims:
                for i, claim in enumerate(top_claims[:3]):
                    st.write(f"{i+1}. \"{claim['text'][:40]}...\" (seen {claim['seen_count']}x)")
            else:
                st.write("No claims yet")
        
        # Latency comparison if we have data
        if st.session_state.cache_latencies or st.session_state.web_latencies:
            st.markdown("---")
            st.markdown("**⏱️ Latency Comparison (This Session):**")
            lat_col1, lat_col2 = st.columns(2)
            with lat_col1:
                if st.session_state.cache_latencies:
                    avg_cache = sum(st.session_state.cache_latencies) / len(st.session_state.cache_latencies)
                    st.success(f"💾 Cache hits: {avg_cache:.2f}s avg ({len(st.session_state.cache_latencies)} queries)")
                else:
                    st.info("💾 No cache hits yet")
            with lat_col2:
                if st.session_state.web_latencies:
                    avg_web = sum(st.session_state.web_latencies) / len(st.session_state.web_latencies)
                    st.warning(f"🌐 Web searches: {avg_web:.2f}s avg ({len(st.session_state.web_latencies)} queries)")
                else:
                    st.info("🌐 No web searches yet")
    
    st.markdown("---")


@st.cache_resource
def load_pipeline():
    """Load and cache the verification pipeline."""
    try:
        # Check for TAVILY_API_KEY specifically as it's optional but critical for full functionality
        if not os.getenv("TAVILY_API_KEY"):
            st.warning("⚠️ TAVILY_API_KEY not found. Web search will be disabled.")
            
        validate_config()
        pipeline = ClaimVerificationPipeline()
        return pipeline
    except Exception as e:
        st.error(f"Failed to initialize pipeline: {e}")
        return None


@st.cache_resource
def load_memory_agent():
    """Load and cache the memory agent."""
    try:
        return MemoryUpdateAgent()
    except Exception as e:
        st.error(f"Failed to initialize memory agent: {e}")
        return None


@st.cache_resource
def get_retriever():
    """Load and cache the retrieval agent for dashboard stats."""
    try:
        return RetrievalAgent()
    except Exception as e:
        st.error(f"Failed to initialize retriever: {e}")
        return None


def render_verdict(verdict: str, confidence: float):
    """Render the verdict with appropriate styling."""
    css_class = {
        "True": "verdict-true",
        "False": "verdict-false",
        "Uncertain": "verdict-uncertain"
    }.get(verdict, "verdict-uncertain")
    
    emoji = {
        "True": "✅",
        "False": "❌",
        "Uncertain": "❓"
    }.get(verdict, "❓")
    
    st.markdown(f"""
    <div class="{css_class}">
        {emoji} {verdict} <span style="font-size: 1rem; opacity: 0.9;">({confidence:.0%} confidence)</span>
    </div>
    """, unsafe_allow_html=True)


def render_evidence_card(evidence: dict, index: int):
    """Render a single evidence card."""
    verdict_color = {
        "True": "#10b981",
        "False": "#ef4444",
        "Uncertain": "#f59e0b"
    }.get(evidence.get("verdict", ""), "#6b7280")
    
    st.markdown(f"""
    <div class="evidence-card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
            <span style="font-weight: 600;">Evidence #{index + 1}</span>
            <span style="background: {verdict_color}; color: white; padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.8rem;">
                {evidence.get("verdict", "Unknown")}
            </span>
        </div>
        <p style="margin: 0.5rem 0; color: #374151;">{evidence.get("claim_text", "")[:200]}...</p>
        <div style="display: flex; gap: 1rem; font-size: 0.85rem; color: #6b7280;">
            <span>📊 Similarity: {evidence.get("similarity_score", 0):.2f}</span>
            <span>📁 Source: {evidence.get("source", "Unknown")}</span>
            <span>👁️ Seen: {evidence.get("seen_count", 0)}x</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def main():
    """Main application."""
    init_session_state()
    
    # Header
    st.markdown('<h1 class="main-header">🔍 Persistent Claim Memory</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">AI-Powered Misinformation Detection with Evolving Memory</p>', unsafe_allow_html=True)
    
    # Main content
    pipeline = load_pipeline()
    
    if not pipeline:
        st.error("⚠️ Pipeline failed to initialize. Check your API keys in `.env`")
        st.code("""
# Required environment variables:
QDRANT_URL=your_qdrant_cloud_url
QDRANT_API_KEY=your_qdrant_api_key
GROQ_API_KEY=your_groq_api_key
GEMINI_API_KEY=your_gemini_api_key  # Optional, for images
        """)
        return
    
    # Live Memory Dashboard - PROVES memory evolution to judges
    retriever = get_retriever()  # Use cached retriever
    if retriever:
        render_memory_dashboard(retriever)
    
    # Input section
    st.markdown("### 📝 Enter a Claim to Verify")
    
    # Initialize claim_input in session state
    if 'claim_input' not in st.session_state:
        st.session_state.claim_input = ""
    if 'auto_verify' not in st.session_state:
        st.session_state.auto_verify = False
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        claim_text = st.text_area(
            "Claim Text",
            value=st.session_state.claim_input,
            placeholder="Enter a claim to verify, e.g., 'Vaccines cause autism in children'",
            height=100,
            max_chars=2000,  # SECURITY: Limit input length
            label_visibility="collapsed",
            key="claim_text_input"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "📷 Upload Image",
            type=["png", "jpg", "jpeg"],
            help="Optional: Upload an image containing a claim"
        )
    
    # Quick examples - clicking sets the claim and triggers auto-verify
    st.markdown("**Quick Examples:**")
    example_cols = st.columns(4)
    examples = [
        "Vaccines cause autism",
        "The Earth is flat",
        "Climate change is a hoax",
        "5G causes COVID-19"
    ]
    
    for i, example in enumerate(examples):
        if example_cols[i].button(example, key=f"ex_{i}", use_container_width=True):
            st.session_state.claim_input = example
            st.session_state.auto_verify = True
            st.rerun()
    
    # Verify button OR auto-verify from quick example
    should_verify = st.button("🔍 Verify Claim", type="primary", use_container_width=True)
    
    if should_verify or st.session_state.auto_verify:
        # Determine which claim to use
        # If auto-verify (from button click), use the stored example
        # Otherwise use the text area content
        if st.session_state.auto_verify:
            final_claim = st.session_state.claim_input
        else:
            final_claim = claim_text if claim_text.strip() else st.session_state.claim_input
        
        # Reset auto-verify flag
        st.session_state.auto_verify = False
        
        if not final_claim.strip():
            st.warning("Please enter a claim to verify")
        else:
            # SECURITY: Simple rate limiting (10 requests per minute per session)
            if 'request_times' not in st.session_state:
                st.session_state.request_times = []
            
            import time as time_module
            current_time = time_module.time()
            # Remove requests older than 60 seconds
            st.session_state.request_times = [
                t for t in st.session_state.request_times 
                if current_time - t < 60
            ]
            
            if len(st.session_state.request_times) >= 10:
                st.error("⚠️ Rate limit exceeded. Please wait a minute before making more requests.")
            else:
                st.session_state.request_times.append(current_time)
                
                with st.spinner("🔄 Analyzing claim..."):
                    try:
                        # Save uploaded image temporarily if present
                        image_path = None
                        if uploaded_file:
                            # SECURITY: Validate file size (max 5MB)
                            MAX_IMAGE_SIZE = 5 * 1024 * 1024
                            file_size = len(uploaded_file.read())
                            uploaded_file.seek(0)  # Reset file pointer
                            
                            if file_size > MAX_IMAGE_SIZE:
                                st.error(f"Image too large. Maximum size is {MAX_IMAGE_SIZE // (1024*1024)}MB.")
                                st.stop()
                            
                            import tempfile
                            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as f:
                                f.write(uploaded_file.read())
                                image_path = f.name
                        
                        # Track latency for dashboard
                        start_time = time.time()
                        
                        # Run verification
                        result = pipeline.verify(text=final_claim, image_path=image_path)
                        
                        # Record latency
                        latency = time.time() - start_time
                        st.session_state.total_queries += 1
                        
                        if result.get("cache_hit"):
                            st.session_state.cache_hits += 1
                            st.session_state.cache_latencies.append(latency)
                        else:
                            st.session_state.web_searches += 1
                            st.session_state.web_latencies.append(latency)
                        
                        st.session_state.last_result = result
                        # Store latency in result for display
                        st.session_state.last_result['latency'] = latency
                        
                        # Clear the input after successful verification
                        st.session_state.claim_input = ""
                        
                        # Add to history
                        st.session_state.verification_history.append({
                            "timestamp": datetime.now().isoformat(),
                            "claim": final_claim[:50],
                            "verdict": result.get("verification", {}).get("verdict", "Unknown"),
                            "confidence": result.get("verification", {}).get("confidence", 0),
                            "cache_hit": result.get("cache_hit", False),
                            "latency": f"{latency:.2f}s"
                        })
                        
                    except Exception as e:
                        st.error(f"Verification failed: {e}")
    
    # Results display
    if st.session_state.last_result:
        result = st.session_state.last_result
        verification = result.get("verification", {})
        
        st.markdown("---")
        st.markdown("### 📋 Verification Results")
        
        # Main verdict
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            render_verdict(
                verification.get("verdict", "Unknown"),
                verification.get("confidence", 0)
            )
        
        with col2:
            memory = result.get("memory", {})
            action = memory.get("action", "unknown")
            seen_count = memory.get("seen_count", 0)
            
            if action == "updated":
                st.markdown(f"""
                <div class="memory-update">
                    🔄 Memory Updated - Seen {seen_count} times
                </div>
                """, unsafe_allow_html=True)
            elif action == "created":
                st.markdown(f"""
                <div class="memory-update">
                    ✨ New Claim Added to Memory
                </div>
                """, unsafe_allow_html=True)
        
        with col3:
            # Web search indicator with latency
            latency = result.get('latency', 0)
            web_search_used = result.get("web_search_used")
            cache_hit = result.get("cache_hit")
            
            if web_search_used:
                st.success(f"🌐 Web Search ({latency:.2f}s)")
            elif cache_hit:
                st.info(f"💾 Cache Hit ({latency:.2f}s)")
            else:
                # Neither cache hit nor web search used -> implying web search failed or disabled
                if latency:
                    st.caption(f"⏱️ {latency:.2f}s")
                
                # Explicit warning if it looked like a cache miss but no web search happened
                if not cache_hit and not web_search_used:
                    st.markdown("⚠️ **Web Search Skipped**")
                    st.caption("(Check API Key)")
            
            normalized = result.get("normalized_claim", {})
            if normalized.get("entities"):
                st.caption(f"Entities: {', '.join(normalized.get('entities', [])[:3])}")
        
        # Explanation
        st.markdown("#### 💭 Reasoning")
        st.info(verification.get("explanation", "No explanation available"))
        
        if verification.get("reasoning_trace"):
            with st.expander("🔍 Detailed Reasoning Trace"):
                st.markdown(verification.get("reasoning_trace"))
        
        # Evidence
        evidence = result.get("evidence", [])
        if evidence:
            # Filter evidence by relevance
            # Only show evidence with similarity > 0.4 OR if it's a cache hit
            relevant_evidence = [
                e for e in evidence 
                if e.get("similarity_score", 0) > 0.4 or result.get("cache_hit")
            ]
            
            if relevant_evidence:
                st.markdown(f"#### 📚 Evidence ({len(relevant_evidence)} relevant claims)")
                for i, ev in enumerate(relevant_evidence[:5]):
                    render_evidence_card(ev, i)
            else:
                if result.get("web_search_used"):
                     st.info("ℹ️ No relevant past claims found in memory. Verdict based on live web search.")
                else:
                     st.warning("⚠️ No relevant knowledge found in memory or web search.")
        
        # Errors
        if result.get("errors"):
            with st.expander("⚠️ Warnings"):
                for error in result["errors"]:
                    st.warning(error)
    
    # History section with enhanced columns
    if st.session_state.verification_history:
        st.markdown("---")
        st.markdown("### 📜 Verification History")
        
        df = pd.DataFrame(st.session_state.verification_history[-10:][::-1])
        df["confidence"] = df["confidence"].apply(lambda x: f"{x:.0%}")
        # Add cache indicator column
        if "cache_hit" in df.columns:
            df["source"] = df["cache_hit"].apply(lambda x: "💾 Cache" if x else "🌐 Web")
        
        column_config = {
            "timestamp": "Time",
            "claim": "Claim",
            "verdict": "Verdict",
            "confidence": "Confidence"
        }
        
        # Add new columns if they exist
        if "source" in df.columns:
            column_config["source"] = "Source"
        if "latency" in df.columns:
            column_config["latency"] = "Latency"
        
        # Select columns to display
        display_cols = ["timestamp", "claim", "verdict", "confidence"]
        if "source" in df.columns:
            display_cols.append("source")
        if "latency" in df.columns:
            display_cols.append("latency")
        
        st.dataframe(
            df[display_cols],
            column_config=column_config,
            hide_index=True,
            use_container_width=True
        )


if __name__ == "__main__":
    main()
