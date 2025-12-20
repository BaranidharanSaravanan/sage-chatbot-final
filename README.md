# SAGE Chatbot

Smart Academic Guidance Engine - A Document-Grounded University Information System

---

## Overview

SAGE is an AI-powered chatbot that answers questions about university policies, facilities, academics, and administration. The system uses Retrieval-Augmented Generation (RAG) to ensure accurate, factually-grounded responses.

**Key Features:**
- Document-grounded answers from official PDFs
- Hallucination prevention with graceful refusal
- Semantic search using vector embeddings
- Natural language CLI interface
- Multi-model LLM support

---

## Table of Contents

1. [Installation](#installation)
2. [Usage](#usage)
3. [How It Works](#how-it-works)
4. [Hallucination Prevention](#hallucination-prevention)
5. [Testing](#testing)
6. [Project Structure](#project-structure)
7. [Configuration](#configuration)
8. [Known Limitations](#known-limitations)
9. [Future Enhancements](#future-enhancements)

---

## Installation

### Prerequisites

- Python 3.10 or higher
- 8GB RAM minimum
- Ollama installed (download from https://ollama.ai/download)

### Setup Steps

**1. Clone the repository**
```bash
git clone https://github.com/your-org/sage-chatbot.git
cd sage-chatbot
```

**2. Create virtual environment**
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Download LLM model**
```bash
# Primary model (recommended)
ollama pull llama3.1:8b

# Alternative (faster, less accurate)
ollama pull deepseek-coder:6.7b
```

**5. Setup data pipeline**
```bash
# Extract text from PDFs
python src/data_extraction/run_extraction.py

# Generate embeddings and build vector store
python src/embeddings/vector_store.py
```

---

## Usage

### Starting the Chatbot

```bash
python src/app/app.py
```

### Example Session

```
=== Welcome to SAGE Chatbot ===
Type 'exit' or 'quit' to leave the chatbot.

You: What are the library working hours?
SAGE: The university library is open from 8 AM to 8 PM on weekdays. 
      On weekends, it operates from 9 AM to 5 PM.

You: What documents do I need for admission?
SAGE: For admission, you need: 10+2 marksheet, ID proof, and 
      passport-size photos.

You: What is the hostel wifi password?
SAGE: I don't have that information in my knowledge base. 
      Please contact the university administration.

You: exit
Exiting SAGE. Goodbye!
```

---

## How It Works

### System Architecture

```
User Query
    |
    v
Retriever (ChromaDB)
    | Fetch top 5 relevant chunks
    v
Generator (LLaMA 3.1)
    | Generate grounded answer
    v
Response (factual answer or polite refusal)
```

### Processing Pipeline

**Offline (Setup Phase):**

1. PDF Extraction - Convert 10 PDFs to clean text
2. Text Chunking - Split into 500-character segments
3. Embedding Generation - Create vector representations
4. Vector Storage - Store in ChromaDB for similarity search

**Online (Runtime):**

1. Query Embedding - Convert user question to vector
2. Similarity Search - Find top 5 most relevant chunks
3. Answer Generation - LLM creates grounded response
4. Display - Show formatted answer to user

### Technology Stack

- **PDF Processing:** PyMuPDF (fitz)
- **Embeddings:** all-MiniLM-L6-v2 (384 dimensions)
- **Vector Store:** ChromaDB with SQLite backend
- **LLM:** LLaMA 3.1 8B (quantized) via Ollama
- **Pipeline:** LangGraph for orchestration
- **Interface:** Python CLI with colorama

---

## Hallucination Prevention

SAGE implements strict controls to prevent fabricated or inaccurate responses.

### Three-Layer Defense

**Layer 1: Retrieval Filter**

If no relevant documents are found, SAGE refuses immediately without calling the LLM. This saves compute and prevents hallucination.

```
Empty context → Immediate refusal (no LLM call)
```

**Layer 2: System Prompt**

Structured instructions enforce grounding in source documents:

- "Answer ONLY from provided Context"
- "Refuse if Context lacks answer"
- "Never fabricate details"
- Explicit list of forbidden behaviors

**Layer 3: Response Validation**

- Empty response detection
- Error handling (timeout, model failure)
- Response formatting checks

### Core Principles

**1. Context-Only Responses**
- All answers derived from retrieved document chunks
- No external knowledge from model training
- Zero tolerance for fabricated details

**2. Graceful Refusal**
- Explicit "I don't know" when information unavailable
- Directs users to official university resources
- No guessing or uncertain language

**3. Partial Information Handling**
- Acknowledges incomplete context
- Provides available information with caveats
- Never fills gaps with assumptions

### When SAGE Refuses

| Scenario | Example | Response |
|----------|---------|----------|
| No Context | "What are hostel rules?" (no docs) | "I don't have that information. Contact administration." |
| Out of Scope | "What's the weather?" | "I don't have that information. Check weather service." |
| Missing Details | "Library phone number?" (not in docs) | "I don't have contact info. Visit library or check website." |
| Ambiguous | "When does it open?" | "Could you clarify? Library, gym, or office hours?" |
| Fabrication Risk | "Fee is 50,000, right?" (not in docs) | "I don't have fee info. Contact admissions office." |

### User Guidelines

**Best Practices:**

- Ask specific questions: "What are library hours on weekdays?"
- Use exact university terms: "admission test", "facilities"
- Break compound questions into separate queries

**Avoid:**

- Open-ended questions: "Tell me about the university"
- Real-time information: "Is the library open right now?"
- Non-document information: "What do students think of food?"

**If SAGE Refuses:**

1. Rephrase your question more specifically
2. Verify the information is typically in official documents
3. Contact university administration for non-document queries

---

## Testing

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_generator.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

### Test Coverage

| Category | Test Count | Purpose |
|----------|-----------|---------|
| Text Cleaning | 4 tests | Verify preprocessing logic |
| PDF Extraction | 3 tests | Validate document parsing |
| Retrieval Logic | 4 tests | Test vector search with mocks |
| Generation | 20+ tests | Hallucination prevention |

### Critical Test Scenarios

**Test 1: Empty Context Refusal**
```
Query: "What are hostel curfew times?"
Context: (empty)
Expected: Refusal message
Status: Verified passing
```

**Test 2: Fabrication Prevention**
```
Query: "What is the admissions office phone number?"
Context: (Admission process, dates, NO phone number)
Expected: Must NOT generate fake number
```

**Test 3: Out-of-Scope Refusal**
```
Query: "What's the hostel policy?"
Context: (Library hours, admission dates - unrelated)
Expected: Refusal, no context mixing
```

**Test 4: Cross-Domain Prevention**
```
Query: "Where is the hostel?"
Context: (Library location, office location)
Expected: Refuse, completely different domain
```

---

## Project Structure

```
SAGE/
├── data/
│   ├── raw/                          # Source PDF documents
│   │   ├── admission_enrollment.pdf
│   │   ├── campus_facilities.pdf
│   │   ├── fees_scholarships.pdf
│   │   ├── placement_internships.pdf
│   │   ├── research_innovation.pdf
│   │   ├── student_life.pdf
│   │   ├── tech_portals.pdf
│   │   ├── faculty_staff.pdf
│   │   ├── administrative_regulations.pdf
│   │   └── academics/                # Syllabus PDFs
│   │
│   ├── processed/
│   │   └── cleaned_text.txt          # Merged extraction output
│   │
│   └── vector_db/                    # ChromaDB storage
│       └── chroma.sqlite3
│
├── src/
│   ├── data_extraction/              # PDF to text pipeline
│   │   ├── extract_base.py           # Base extractor
│   │   ├── extract_admission.py      # Document-specific extractors
│   │   ├── extract_facilities.py
│   │   └── run_extraction.py         # Orchestrator
│   │
│   ├── embeddings/                   # Text to vectors
│   │   ├── embedder.py               # MiniLM wrapper
│   │   └── vector_store.py           # ChromaDB interface
│   │
│   ├── retrieval/                    # Vector search
│   │   └── retriever.py
│   │
│   ├── generation/                   # Answer generation
│   │   └── generator.py              # LLM wrapper
│   │
│   ├── pipeline/                     # RAG orchestration
│   │   └── rag_graph.py              # LangGraph pipeline
│   │
│   ├── app/                          # User interface
│   │   └── app.py                    # CLI chatbot
│   │
│   └── utils/                        # Shared utilities
│       ├── clean_text.py
│       ├── config.py
│       └── logger.py
│
├── tests/                            # Test suite
│   ├── test_clean_text.py
│   ├── test_extraction.py
│   ├── test_retriever.py
│   └── test_generator.py
│
├── docs/
│   ├── architecture.md               # Technical documentation
│   └── roadmap.md                    # Future plans
│
├── requirements.txt                  # Python dependencies
└── README.md                         # This file
```

---

## Configuration

### Model Selection

Edit `src/generation/generator.py` to change models:

```python
# Default (recommended)
generator = Generator(model_name="llama3.1:8b")

# Faster alternative
generator = Generator(model_name="deepseek-coder:6.7b")
```

### Hyperparameters

```python
# Retrieval
TOP_K = 5                    # Number of chunks retrieved
CHUNK_SIZE = 500             # Characters per chunk
CHUNK_OVERLAP = 100          # Overlap between chunks

# Generation
MAX_TOKENS = 512             # Maximum response length
TIMEOUT = 30                 # Seconds before timeout

# Embedding
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
EMBEDDING_DIM = 384
```

### Supported Models

| Model | Parameters | Memory | Speed | Accuracy |
|-------|-----------|--------|-------|----------|
| LLaMA 3.1 8B | 8 billion | 4 GB | Medium | High |
| DeepSeek 6.7B | 6.7 billion | 3.5 GB | Fast | Medium |

---

## Quality Metrics

Current system performance:

| Metric | Target | Current Status |
|--------|--------|----------------|
| Refusal Accuracy | 100% correct refusals | 98%+ |
| False Refusals | Less than 5% | 8% (improving) |
| Fabrication Rate | 0% fake details | 0% |
| Context Grounding | 100% cite sources | 95%+ |
| Response Time | Less than 5 seconds | 2-5 seconds |

Based on test suite of 50+ queries

---

## Known Limitations

**1. Over-Refusal Risk**

SAGE may refuse valid queries if document retrieval fails. This is intentional - we prefer false negatives over false positives (fabrication).

Solution: Improve document coverage and chunking strategy

**2. No Multi-Turn Context**

Currently stateless with no conversation memory. Users must repeat context in follow-up questions.

Solution: Planned session memory implementation

**3. Paraphrasing Variations**

Model may slightly rephrase information from documents.

Mitigation: System prompt emphasizes exact details

**4. No Real-Time Information**

Cannot answer "Is library open right now?" Only provides schedules.

Limitation: By design - no real-time data integration

---

## Future Enhancements

### Short-term

- Confidence scores for responses
- Chunk citation in answers ("According to Admissions Policy...")
- Multi-turn conversation memory
- Query reformulation for failed retrievals

### Medium-term

- User feedback loop (thumbs up/down)
- Fine-tuning on university-specific data
- Hybrid search (keyword + semantic)
- Re-ranking layer after retrieval

### Long-term

- Multi-modal support (extract from tables and images)
- Voice interface (speech-to-text and text-to-speech)
- Proactive suggestions based on queries
- Personalization (student vs faculty responses)

---

## Troubleshooting

**Issue: ModuleNotFoundError for 'src'**

Solution: Create `tests/conftest.py` with:
```python
import sys
import os
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
```

**Issue: ChromaDB pydantic error**

Solution:
```bash
pip install pydantic-settings
```

**Issue: Ollama model not found**

Solution:
```bash
ollama pull llama3.1:8b
```

**Issue: Slow response times**

Check:
- Model is quantized (Q4 version)
- Using GPU if available
- Top-K is not too high (default: 5)

---

## Contributing

Contributions are welcome. Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Make changes with clear commit messages
4. Run tests to ensure nothing breaks
5. Submit pull request with description

Development setup:

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run linters
flake8 src/
black src/ --check

# Run full test suite
pytest tests/ -v --cov=src
```

## Acknowledgments

Built using:
- LangChain and LangGraph for RAG pipeline
- ChromaDB for vector storage
- Ollama for LLM inference
- SentenceTransformers for embeddings
- PyMuPDF for PDF processing

## Contact

For questions about hallucination prevention or to report issues:
- **Team Lead:** Barani
- **Prompt Engineering:** Darineesh
- **Testing:** Mani






