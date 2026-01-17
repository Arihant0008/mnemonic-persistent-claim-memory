# 🏗️ PCM System Architecture - Technical Documentation

> **Persistent Claim Memory (PCM)** - A Multi-Agent Misinformation Detection System with Evolving Memory

---

## 📌 Executive Summary

PCM is a **cache-first, web-augmented fact-checking system** that learns from every verification. It solves a fundamental problem in misinformation detection: **redundant verification of the same claims**.

**Core Innovation**: Instead of treating each fact-check as independent, PCM maintains a persistent vector memory that grows smarter with every query. Repeated claims get instant answers; new claims trigger web search and then get stored for future use.

---

## 🧠 Why This Architecture?

### The Problem We're Solving

Traditional fact-checking systems have three critical flaws:

| Problem | Traditional Approach | PCM Solution |
|---------|---------------------|--------------|
| **Amnesia** | Every query starts from scratch | Persistent vector memory remembers all verified claims |
| **Latency** | 3-8 seconds per web search | <200ms for cached claims |
| **Cost** | Every query = API call | 99% reduction for popular claims |

### Why Multi-Agent?

We chose a **multi-agent architecture** (not a single monolithic model) because:

1. **Separation of Concerns**: Each agent does one thing well
2. **Debuggability**: Easy to trace which agent caused an issue
3. **Modularity**: Can swap out any agent without rewriting others
4. **Scalability**: Agents can be scaled independently

---

## 🔄 System Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              USER INPUT                                  │
│                    (Text claim, Image, or Both)                         │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  AGENT 1: NORMALIZER                                                     │
│  ─────────────────────────────────────────────────────────────────────  │
│  Input:  "Did u kno vaccines cause AUTISM??? 🤔💉"                       │
│  Output: "Vaccines cause autism in children"                             │
│                                                                          │
│  WHY: Messy social media text → clean, comparable format                │
│  TECH: Groq (Llama 3.1-8B) for text, Gemini Flash for images            │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  AGENT 2: RETRIEVER (Memory Check)                                       │
│  ─────────────────────────────────────────────────────────────────────  │
│  Input:  Normalized claim text                                           │
│  Output: Top-10 similar claims from database + similarity scores         │
│                                                                          │
│  DECISION POINT:                                                         │
│  • similarity ≥ 0.85 AND age ≤ 3 days → CACHE HIT (skip web search)     │
│  • otherwise → CACHE MISS (proceed to web search)                        │
│                                                                          │
│  WHY: Avoid redundant web searches for known claims                      │
│  TECH: Qdrant vector database + FastEmbed (all-MiniLM-L6-v2)            │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │
                    ┌───────────┴───────────┐
                    │                       │
              CACHE HIT               CACHE MISS
                    │                       │
                    │                       ▼
                    │     ┌─────────────────────────────────────────────┐
                    │     │  AGENT 3: WEB SEARCHER                      │
                    │     │  ───────────────────────────────────────── │
                    │     │  Input:  Normalized claim                   │
                    │     │  Output: 5 fact-check sources with content  │
                    │     │                                             │
                    │     │  WHY: Get fresh evidence for new/stale     │
                    │     │       claims from authoritative sources     │
                    │     │  TECH: Tavily API (AI-optimized search)    │
                    │     │  PRIORITY: Snopes, Reuters, PolitiFact     │
                    │     └─────────────────┬───────────────────────────┘
                    │                       │
                    └───────────┬───────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  AGENT 4: REASONER                                                       │
│  ─────────────────────────────────────────────────────────────────────  │
│  Input:  Claim + Memory evidence + Web search results (if any)          │
│  Output: Verdict (True/False/Uncertain) + Confidence + Explanation       │
│                                                                          │
│  WHY: LLM reasoning combines all evidence into a coherent judgment       │
│  TECH: Groq (Llama 3.1-8B) with chain-of-thought prompting              │
│                                                                          │
│  VERDICT RULES:                                                          │
│  • "True" = The claim IS factually correct                              │
│  • "False" = The claim IS factually incorrect (misinformation)          │
│  • "Uncertain" = Insufficient evidence to determine                      │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  AGENT 5: MEMORY UPDATER                                                 │
│  ─────────────────────────────────────────────────────────────────────  │
│  Input:  Verification result                                             │
│  Output: Memory action (created/updated) + claim ID                      │
│                                                                          │
│  LOGIC:                                                                  │
│  • If similar claim exists (≥0.92 similarity): UPDATE seen_count++      │
│  • Otherwise: INSERT new claim with verdict                              │
│                                                                          │
│  WHY: Build persistent knowledge base for future queries                 │
│  TECH: Qdrant upsert operations                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 📁 Codebase Structure

```
pmc-opus-anti/
│
├── 📄 app.py                      # Streamlit web interface
├── 📄 cli.py                      # Command-line interface  
├── 📄 requirements.txt            # Python dependencies
├── 📄 .env                        # API keys (NEVER commit this!)
├── 📄 README.md                   # Quick start guide
│
├── 📁 src/                        # Core logic
│   ├── 📄 __init__.py             # Package marker
│   ├── 📄 config.py               # Centralized configuration
│   ├── 📄 pipeline.py             # LangGraph orchestration
│   ├── 📄 data_ingestion.py       # Initial data loading
│   │
│   └── 📁 agents/                 # The five agents
│       ├── 📄 __init__.py         # Agent exports
│       ├── 📄 normalizer.py       # Agent 1: Text/Image cleanup
│       ├── 📄 retriever.py        # Agent 2: Vector search
│       ├── 📄 web_search.py       # Agent 3: Tavily web search
│       ├── 📄 reasoner.py         # Agent 4: LLM reasoning
│       └── 📄 memory.py           # Agent 5: Memory updates
│
├── 📁 .streamlit/                 # Streamlit theming
│   └── 📄 config.toml             # Dark theme configuration
│
├── 📁 docs/                       # Documentation
│   ├── 📄 ARCHITECTURE_PROFESSIONAL.md  # This file
│   └── 📄 ARCHITECTURE_SIMPLE.md        # ELI5 version
│
├── 📁 tests/                      # Test suite
│   └── 📄 test_agents.py          # Agent unit tests
│
└── 📁 data/                       # Runtime data
    └── 📁 cache/                  # Local cache directory
```

---

## 📄 File-by-File Deep Dive

### `app.py` - Web Interface

**Purpose**: Beautiful Streamlit dashboard for non-technical users.

**Key Components**:
- Custom CSS for gradient headers, verdict cards, evidence cards
- Session state for verification history
- Quick example buttons with auto-verify
- Real-time loading spinners
- Cache hit/web search indicators

**Why Streamlit?** 
- Rapid prototyping (hours, not days)
- Built-in state management
- Beautiful default components
- Easy deployment

---

### `cli.py` - Command Line Interface

**Purpose**: Developer-friendly interface for scripting and testing.

**Commands**:
```bash
python cli.py verify "Vaccines cause autism"  # Verify claim
python cli.py stats                           # Database stats
python cli.py ingest                          # Load initial data
python cli.py clear --force                   # Reset database
python cli.py run                             # Start web UI
```

**Why CLI?**
- Faster for development/debugging
- Scriptable for batch processing
- Backup interface if UI fails

---

### `src/config.py` - Configuration Hub

**Purpose**: Single source of truth for all settings.

**Key Settings**:
```python
# Thresholds
CACHE_HIT_THRESHOLD = 0.85    # How similar for cache hit?
CACHE_MAX_AGE_DAYS = 3        # When to refresh stale claims?
SIMILARITY_THRESHOLD = 0.92   # When to deduplicate?

# Models
TEXT_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
GROQ_MODEL = "llama-3.1-8b-instant"
```

**Why Centralized Config?**
- Easy tuning without code changes
- Clear documentation of magic numbers
- Environment-based overrides

---

### `src/pipeline.py` - Orchestration Layer

**Purpose**: Connects agents in the correct order using LangGraph.

**State Machine**:
```
normalizer → retriever → web_search → reasoner → memory → END
```

**Why LangGraph?**
- Clean state management between agents
- Visualizable flow diagrams
- Easy to add conditional branches
- Built-in observability

---

### `src/agents/normalizer.py` - Input Cleanup

**Purpose**: Transform noisy input into clean, comparable claims.

**Capabilities**:
1. **Text normalization**: Remove emojis, fix typos, standardize phrasing
2. **Entity extraction**: Identify key subjects (people, places, topics)
3. **Image OCR**: Extract text from images using Gemini Vision

**Why Two Models?**
- Groq (Llama): Fast, cheap text processing
- Gemini: Best-in-class image understanding

---

### `src/agents/retriever.py` - Vector Search

**Purpose**: Find similar claims in persistent memory.

**Features**:
1. **Semantic Search**: Find claims by meaning, not keywords
2. **Time Decay**: Recent claims ranked higher (Gaussian decay, σ=90 days)
3. **Discovery Search**: Find contradicting claims using anchor embeddings

**Why Qdrant?**
- Free cloud tier (1GB)
- Named vectors (text + visual)
- Atomic payload updates
- Fast similarity search

**Time Decay Formula**:
```
decay = e^(-(days_old²) / (2 × 90²))
score = base_score × (0.5 + 0.5 × decay)
```

---

### `src/agents/web_search.py` - Internet Search

**Purpose**: Get fresh evidence for new or stale claims.

**Features**:
- Searches multiple sources simultaneously
- Prioritizes fact-checking sites (Snopes, Reuters, PolitiFact)
- Excludes unreliable sources (Reddit, Twitter, TikTok)

**Why Tavily?**
- Designed for AI agents (structured output)
- Optimized for factual queries
- Direct answers when available

---

### `src/agents/reasoner.py` - LLM Reasoning

**Purpose**: Synthesize evidence into a verdict using chain-of-thought.

**Critical framing**: The LLM is a **synthesizer, not a source**. It combines evidence from memory and web search — it does not invent facts.

**Input Sources**:
1. Memory evidence (similar verified claims)
2. Web search results (if cache miss)

**Output**:
```json
{
  "verdict": "False",
  "confidence": 0.92,
  "explanation": "Multiple peer-reviewed studies have debunked this claim...",
  "reasoning_trace": "Step 1: Examined 3 similar claims in memory..."
}
```

**Why Groq?**
- Fastest LLM inference (100+ tokens/sec)
- Free tier (60 requests/min)
- Llama 3.1 quality

**Understanding Confidence Scores**:

> **Confidence ≠ probability of truth. Confidence = synthesis strength.**

| Confidence measures | Confidence does NOT measure |
|---------------------|----------------------------|
| Source agreement (how many sources support verdict) | Statistical probability of correctness |
| Memory consensus (do cached claims agree?) | Guarantee of factual accuracy |
| Evidence quality (reliability of sources) | LLM's internal certainty (often miscalibrated) |

| Score | Interpretation |
|-------|---------------|
| 90%+ | Strong consensus across multiple authoritative sources |
| 70-89% | Majority agreement with some caveats |
| 50-69% | Mixed signals, verdict reflects best available evidence |
| <50% | Insufficient evidence → "Uncertain" verdict |

---

### `src/agents/memory.py` - Persistent Storage

**Purpose**: Store verified claims for future queries.

**Logic**:
```
IF similarity(new_claim, existing_claim) >= 0.92:
    UPDATE existing_claim.seen_count++
ELSE:
    INSERT new_claim
```

**Stored Fields**:
- `claim_text`, `normalized_text`
- `verdict`, `confidence`, `explanation`
- `source`, `source_reliability`
- `seen_count`, `first_seen`, `last_seen`

---

## ⚙️ Technology Choices Explained

| Technology | Purpose | Why This One? |
|------------|---------|---------------|
| **Qdrant** | Vector database | Free cloud, named vectors, atomic updates |
| **LangGraph** | Orchestration | Clean state flow, easy debugging |
| **Groq** | LLM inference | Fastest free tier, Llama 3.1 quality |
| **Tavily** | Web search | AI-optimized, fact-check focused |
| **Gemini** | Image OCR | Best vision model, free tier |
| **FastEmbed** | Embeddings | CPU-friendly, no GPU needed |
| **Streamlit** | Web UI | Rapid development, beautiful defaults |

---

## 🔒 Cache Strategy

> **Critical: This is semantic caching, not string caching.**

### Why This Is Not Just Caching

| Regular Cache (Redis, etc.) | PCM Semantic Memory |
|----------------------------|---------------------|
| Exact string match only | **Paraphrases resolve to same memory** |
| "vaccines autism" ≠ "vaccines cause autism" | Both → same cached verdict |
| No understanding of meaning | **Embedding-based similarity** |
| Static TTL | **Temporal decay + freshness checks** |

### When We Use Cache (Skip Web Search)

A claim is considered a **cache hit** when:
1. Similarity to existing claim ≥ 0.85 (very similar meaning)
2. Existing claim age ≤ 3 days (still fresh)

### When We Search the Web

A claim triggers **web search** when:
1. No similar claim exists in memory, OR
2. Best match similarity < 0.85, OR
3. Best match is older than 3 days

### Adversarial Example: Correct Near-Miss Behavior

```
Query A: "Vaccines cause autism"      → similarity: 1.00 → Cache HIT ✓
Query B: "Vaccines cause cancer"      → similarity: 0.82 → Cache MISS ✓  
Query C: "Vaccines prevent disease"   → similarity: 0.71 → Cache MISS ✓
```

**Why this matters:** Queries B and C are about vaccines but have *different factual claims*. Our 0.85 threshold correctly triggers fresh web searches for them instead of returning the wrong cached verdict. This demonstrates restraint, not just optimization.

### Why These Thresholds?

See [`docs/THRESHOLDS.md`](THRESHOLDS.md) for full empirical justification.

- **0.85 similarity**: High enough to avoid false matches, low enough to catch paraphrases
- **3 days freshness**: Balances currency vs API costs
- **0.92 deduplication**: Very strict to avoid merging different claims

---

## 📊 Performance Characteristics

| Operation | Latency | Cost |
|-----------|---------|------|
| Cache Hit | ~200ms | $0 |
| Cache Miss (Web Search) | 3-8 sec | ~$0.001 |
| Memory Stats | ~500ms | $0 |
| Data Ingestion (50 claims) | ~30 sec | $0 |

---

## 🚀 Deployment Options

### Local Development
```bash
pip install -r requirements.txt
streamlit run app.py
```

### Docker
```bash
docker-compose up
```

### Cloud (Streamlit Community Cloud)
1. Push to GitHub
2. Connect at share.streamlit.io
3. Add secrets in dashboard

---

## 🔮 Future Enhancements

1. **Claim categorization**: Separate timeless facts from current events
2. **Source diversity**: Require 3+ sources for high confidence
3. **User feedback loop**: Let users correct verdicts
4. **Batch API**: Process multiple claims in parallel
5. **Browser extension**: Real-time fact-checking on social media

---

*Built for fighting misinformation, one claim at a time.* 🔍
