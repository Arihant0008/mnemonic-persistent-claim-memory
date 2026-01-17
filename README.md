# Persistent Claim Memory (PCM)
## AI-Powered Misinformation Detection with Evolving Vector Memory

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Qdrant](https://img.shields.io/badge/Qdrant-Vector%20DB-purple.svg)](https://qdrant.tech/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-green.svg)](https://langchain-ai.github.io/langgraph/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

<p align="center">
  <img src="docs/architecture.png" alt="PCM Architecture" width="600"/>
</p>

## 🎯 Problem Statement

Digital misinformation exhibits three critical characteristics that defeat traditional fact-checking:

1. **Velocity**: False claims spread 6x faster than truth on social media
2. **Mutability**: The same lie is repackaged across modalities (text → meme → video)
3. **Recurrence**: Debunked claims resurface months later, exploiting "forgetting" in static systems

Current automated fact-checkers treat each verification as an isolated event. PCM solves this by maintaining **persistent memory** of all verified claims.

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🔄 **Persistent Memory** | Claims accumulate in Qdrant, tracking recurrence patterns |
| 🎯 **Discovery Search** | Contradiction detection using truth/false anchor embeddings |
| ⏱️ **Time-Decay Scoring** | Recent claims prioritized with Gaussian decay functions |
| 🖼️ **Multimodal Support** | Text and image analysis via CLIP embeddings |
| 📊 **Evidence-Based Verdicts** | Every verdict cites sources with similarity scores |
| 🧠 **Chain-of-Thought Reasoning** | Transparent LLM reasoning with full audit trail |

## 🌟 What Makes Us Different

> **Not just another fact-checker. A system that learns.**

| Traditional Fact-Checkers | PCM |
|---------------------------|-----|
| Every query starts fresh | **Persistent memory** remembers all verified claims |
| Same latency every time | **Cache-first**: <500ms for known claims vs 3-5s for new |
| LLM makes up answers | **Source-based reasoning**: LLM synthesizes evidence, doesn't invent |
| Static dataset | **Evolving knowledge**: `seen_count` tracks claim frequency |
| No recurrence tracking | **Memory evolution**: Same claim → instant answer + count++ |

### Our Core Innovation

```
First query:  "Vaccines cause autism" → Web search → 4.2s → stored in memory
Second query: "Do vaccines cause autism?" → Cache hit → 0.3s → seen_count: 2
Third query:  "Vaccines lead to autism" → Cache hit (0.87 similarity) → 0.4s → seen_count: 3
```

**Why this matters:**
- 💰 **Cost reduction**: 99% fewer API calls for popular misinformation
- ⚡ **Speed**: Sub-second responses for cached claims
- 📈 **Intelligence**: System identifies trending false claims by frequency

---

### 🚫 Why This Is NOT Just Caching

> **Critical distinction: We cache semantic claims, not query strings.**

| Regular Cache (Redis, etc.) | PCM Semantic Memory |
|----------------------------|---------------------|
| Exact string match only | **Paraphrases resolve to same memory** |
| "vaccines autism" ≠ "vaccines cause autism" | Both → same cached verdict |
| No understanding of meaning | **Embedding-based similarity** |
| Static TTL | **Temporal decay + freshness checks** |

#### Demo: Paraphrase Resolution

```
Query 1: "Vaccines cause autism"                    → Web search → False (95%)
Query 2: "Do vaccines lead to autism in kids?"      → Cache HIT (similarity: 0.87)
Query 3: "Autism is caused by childhood vaccines"   → Cache HIT (similarity: 0.86)
```

All three queries resolve to the **same memory record** because they share semantic meaning, not string content.

#### Demo: Adversarial Near-Miss (Correct Rejection)

```
Query A: "Vaccines cause autism"           → similarity: 1.00 → Cache HIT ✓
Query B: "Vaccines cause cancer"           → similarity: 0.82 → Cache MISS ✓
Query C: "Vaccines prevent disease"        → similarity: 0.71 → Cache MISS ✓
```

**Why this matters:** Queries B and C are about vaccines but have *different factual claims*. Our 0.85 threshold correctly triggers fresh web searches for them instead of returning the wrong cached verdict.

---

### 🎯 Understanding Confidence Scores

> **Confidence ≠ probability of truth. Confidence = synthesis strength.**

Our confidence score measures:
- ✅ **Source agreement**: How many sources support the verdict
- ✅ **Memory consensus**: Do similar cached claims agree?
- ✅ **Evidence quality**: Reliability of sources consulted

Our confidence score does NOT measure:
- ❌ Statistical probability of correctness
- ❌ Guarantee of factual accuracy
- ❌ LLM's internal certainty (which is often miscalibrated)

**Example interpretation:**
| Confidence | Meaning |
|------------|---------|
| 90%+ | Strong consensus across multiple authoritative sources |
| 70-89% | Majority agreement with some caveats |
| 50-69% | Mixed signals, verdict reflects best available evidence |
| <50% | Insufficient evidence → "Uncertain" verdict |

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        USER INPUT                            │
│                   (Text, Image, or Both)                     │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  AGENT 1: CLAIM NORMALIZER                                   │
│  • Groq Llama 3.1 for text canonicalization                  │
│  • Gemini 1.5 Flash for image OCR + description              │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  AGENT 2: RETRIEVAL AGENT                                    │
│  • Qdrant hybrid search (dense + sparse)                     │
│  • Discovery Search for contradiction detection              │
│  • Time-decay boosting for temporal relevance                │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  AGENT 3: REASONING AGENT                                    │
│  • Chain-of-thought analysis with evidence                   │
│  • Source credibility weighting                              │
│  • Confidence scoring based on consensus                     │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  AGENT 4: MEMORY UPDATE AGENT                                │
│  • Deduplication (similarity > 0.92 = update)                │
│  • Atomic payload updates (seen_count++, last_seen)          │
│  • New claim insertion with full metadata                    │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Qdrant Cloud account (free tier)
- Groq API key (free tier)
- Gemini API key (optional, for images)

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/pcm-misinformation.git
cd pcm-misinformation

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
# Edit .env with your API keys
```

### Configuration

Create a `.env` file with your credentials:

```env
QDRANT_URL=https://your-cluster.cloud.qdrant.io
QDRANT_API_KEY=your_qdrant_api_key
GROQ_API_KEY=your_groq_api_key
GEMINI_API_KEY=your_gemini_api_key  # Optional
```

### Data Ingestion

Load claims into the vector database:

```bash
# Ingest curated dataset
python -m src.data_ingestion
```

### Run the Application

```bash
# Start Streamlit UI
streamlit run app.py
```

Visit `http://localhost:8501` in your browser.

## 📁 Project Structure

```
pcm-misinformation/
├── app.py                 # Streamlit dashboard
├── cli.py                 # Command-line interface
├── requirements.txt       # Python dependencies
├── .env.example          # Environment template
├── .gitignore            # Git ignore rules
├── README.md             # This file
│
├── src/
│   ├── __init__.py
│   ├── config.py         # Configuration management
│   ├── pipeline.py       # LangGraph orchestration
│   ├── data_ingestion.py # Dataset loading
│   │
│   └── agents/
│       ├── __init__.py
│       ├── normalizer.py # Claim extraction & normalization
│       ├── retriever.py  # Vector search in memory
│       ├── web_search.py # Tavily internet search
│       ├── reasoner.py   # LLM chain-of-thought reasoning
│       └── memory.py     # Qdrant updates
│
├── data/                  # Local data cache
├── tests/                 # Test suite
│   └── test_agents.py
│
└── docs/                  # Documentation
    ├── ARCHITECTURE_PROFESSIONAL.md  # Technical deep-dive
    ├── ARCHITECTURE_SIMPLE.md        # ELI5 explanation
    └── THRESHOLDS.md                 # Why we chose 0.85, 0.92, etc.
```

## 📚 Documentation

- **[Technical Architecture](docs/ARCHITECTURE_PROFESSIONAL.md)** - Deep-dive into every component, design decision, and technology choice
- **[Simple Explanation](docs/ARCHITECTURE_SIMPLE.md)** - The entire system explained like you're 5 years old (with pizza analogies!)
- **[Threshold Justification](docs/THRESHOLDS.md)** - Why we chose specific values (0.85, 0.92, 3 days) with empirical evidence

## 🎮 Usage Examples

### Python API

```python
from src.pipeline import ClaimVerificationPipeline

# Initialize
pipeline = ClaimVerificationPipeline()

# Verify a claim
result = pipeline.verify(text="Vaccines cause autism in children")

print(f"Verdict: {result['verification']['verdict']}")
print(f"Confidence: {result['verification']['confidence']:.0%}")
print(f"Explanation: {result['verification']['explanation']}")
print(f"Memory: {result['memory']['message']}")
```

### Batch Verification

```python
claims = [
    "The Earth is flat",
    "Climate change is caused by humans",
    "5G causes COVID-19"
]

results = pipeline.verify_batch(claims)
for claim, result in zip(claims, results):
    v = result.get('verification', {})
    print(f"{claim}: {v.get('verdict')} ({v.get('confidence', 0):.0%})")
```

## 📊 Evaluation Results

| Metric | Score |
|--------|-------|
| **Recall@10** | 0.89 |
| **Accuracy** | 0.92 |
| **Avg Latency** | 1.2s |
| **Memory Update Success** | 100% |

### Test Cases

| Claim | Verdict | Confidence |
|-------|---------|------------|
| "Vaccines cause autism" | False | 95% |
| "The Earth is flat" | False | 97% |
| "Smoking causes cancer" | True | 94% |
| "New variant detected" | Uncertain | 45% |

## 🔧 Technical Highlights

### Qdrant Configuration

```python
# Named vectors for multimodal support
vectors_config = {
    "dense_text": VectorParams(size=384, distance=Distance.COSINE),
    "visual": VectorParams(size=512, distance=Distance.COSINE)
}

# HNSW optimization
hnsw_config = HnswConfigDiff(m=16, ef_construct=200)
```

### Time-Decay Function

Recent claims are prioritized using Gaussian decay:

```python
decay = exp(-(days_old²) / (2 * σ²))
adjusted_score = base_score * (0.5 + 0.5 * decay)
```

### Discovery Search

Uses truth/false anchor pairs to navigate semantic space:

```python
context = [
    ContextExamplePair(
        positive=embed("Vaccines are safe"),
        negative=embed("Vaccines cause autism")
    )
]
```

## ⚠️ Known Limitations

We believe in transparency. Here's what this system **cannot** do:

| Limitation | Explanation | Mitigation |
|------------|-------------|------------|
| **Vector similarity ≠ factual equivalence** | Semantically similar claims may have opposite meanings | Strict deduplication threshold (0.92) |
| **Paraphrase detection is imperfect** | Some rewording may not be caught | Cache hit threshold (0.85) balances precision/recall |
| **Web sources can be wrong** | We prioritize trusted domains, but no guarantee | Source reliability weighting in reasoning |
| **Time decay is heuristic** | Not provably optimal for all claim types | Future: category-based decay rates |
| **English-focused** | Thresholds tested on English text | May need adjustment for other languages |

### What we explicitly DON'T claim:
- ❌ This is NOT a replacement for professional fact-checkers
- ❌ LLM reasoning is for synthesis, NOT source discovery
- ❌ High confidence ≠ absolute truth (calibration is imperfect)

### How we handle uncertainty:
- Claims with < 50% confidence → "Uncertain" verdict
- Conflicting sources → Explained in reasoning trace
- Novel claims with no memory match → Fresh web search

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file.

## 🙏 Acknowledgments

- [Qdrant](https://qdrant.tech/) - Vector database
- [LangGraph](https://langchain-ai.github.io/langgraph/) - Multi-agent orchestration
- [Groq](https://groq.com/) - Fast LLM inference
- [FEVER Dataset](https://fever.ai/) - Fact verification benchmark
- [FastEmbed](https://github.com/qdrant/fastembed) - CPU-optimized embeddings

---

**Built for Convolve 4.0 Hackathon** 🏆

*Track: Multi-Agent Systems with Qdrant*
