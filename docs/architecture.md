# SAGE Chatbot - System Architecture
  1.System Overview

SAGE (Smart Academic Guidance Engine) is a Retrieval-Augmented Generation chatbot that answers university queries using verified institutional documents. The system prioritizes factual accuracy through strict hallucination prevention.

Core Principle: Answer only from verified documents. When information is unavailable, refuse gracefully rather than fabricate.

 2.Architecture Flow

User Query
    ↓
Embedding Generation
    ↓
Vector Similarity Search
    ↓
Context Retrieval (Top-5 chunks)
    ↓
LLM Generation with Context
    ↓
Response Validation
    ↓
User Interface

  3.Core Components

- Data Extraction Layer

Transforms PDF documents into clean, structured text for processing.

Technology: PyMuPDF (fitz)

Process:
Reads 10+ university PDF documents, removes headers, footers, and page numbers, normalizes special characters and ligatures, maintains document source attribution, and outputs cleaned text corpus of approximately 150KB.

Location: src/data_extraction/

The extraction layer has document-specific extractors for academics, admission, facilities, and other document types. Each extractor inherits from a base extractor class and applies custom cleaning rules appropriate for its document type.


-- Embedding Layer

Converts text into vector representations for semantic similarity search.

Model: all-MiniLM-L6-v2 (SentenceTransformers)
Dimensions: 384
Framework: Hugging Face Transformers

Chunking Strategy:
Chunk Size: 500 characters
Overlap: 100 characters
Method: Character-based splitting

The overlap preserves context across chunk boundaries, preventing information loss during retrieval.

Location: src/embeddings/


-- Vector Store

Persistent storage for embedded document chunks with efficient similarity search.

Technology: ChromaDB with SQLite backend

Features:
Automatic embedding generation on insertion, cosine similarity search, persistent storage across sessions, and collection-based organization.

Storage: data/vector_db/

The vector store contains approximately 300 chunks with query latency under 100ms.


-- Retrieval Layer

Identifies and retrieves the most relevant document chunks for a query.

Configuration:
Top-K: 5 chunks (default)
Similarity Metric: Cosine similarity
Direct retrieval without re-ranking

Implementation:
The retriever queries ChromaDB with the user's question, retrieves the 5 most similar chunks based on cosine similarity, and returns them for context generation. If no relevant chunks are found, it returns an empty list.

Location: src/retrieval/


-- Generation Layer

Generates contextually grounded answers using retrieved document chunks.

Models:
Primary: LLaMA 3.1 8B (4-bit quantized)
Alternative: DeepSeek 6.7B (4-bit quantized)
Interface: Ollama

System Prompt Structure:

The generator uses a three-section prompt:

Core Rules:
Answer ONLY from provided context
Refuse if context lacks the answer
No assumptions or inferences
No cross-context information mixing
Ask for clarification if ambiguous

Response Guidelines:
Be concise and direct
Cite specific details (times, locations, procedures)
Acknowledge partial information with caveats
Maintain professional tone
Present steps clearly

Forbidden Behaviors:
Never fabricate details (phone numbers, dates, names)
Never answer out-of-scope queries
Never use external knowledge
Never use uncertain language ("I think", "probably")

Safety Mechanism:
Before calling the LLM, the generator checks if context is empty. If no context exists, it immediately returns a refusal message without making an LLM call. This prevents hallucination entirely for out-of-scope queries.

Location: src/generation/


  4.RAG Pipeline

Orchestrates the complete retrieval and generation workflow.

Technology: LangGraph (StateGraph)

State:
question: User query
context: Retrieved document chunks
answer: Generated response

Flow:
User query enters pipeline, retrieve node performs vector search and gets top chunks, generate node constructs prompt with chunks and generates answer, response returned to user.

Location: src/pipeline/


  5.Application Layer

Command-line interface for user interaction.

Features:
Interactive chat loop, colored output (user in cyan, bot in green), session continuity, and graceful exit with exit or quit commands.

Location: src/app/


  6.Utilities Layer

Shared helper functions and configuration.

Components:
clean_text.py for text preprocessing functions
logger.py for structured logging setup
config.py for path definitions and system constants

Location: src/utils/
  7.Setup Phase (Offline)

PDF Extraction:
10+ PDFs go through document extractors to produce cleaned_text.txt of approximately 150KB

Embedding Generation:
cleaned_text.txt is chunked into 500 character pieces with 100 character overlap, producing approximately 300 chunks

Vector Storage:
300 chunks are embedded using MiniLM and stored in ChromaDB


  8.Query Phase (Online)

Query Embedding:
User question like "What are the library hours?" is converted to 384-dimensional vector using MiniLM

Similarity Search:
Query vector is compared against ChromaDB using cosine search to retrieve top 5 chunks

Answer Generation:
Query plus 5 chunks are sent to LLaMA 3.1 which generates grounded answer

Response Display:
Answer is formatted and displayed to user via CLI

Typical Response Time: 2-5 seconds total


  9.Hallucination Prevention

SAGE uses a three-layer defense system.

# Layer 1: Pre-Generation Filter

Before calling the LLM, the system checks if any relevant context was retrieved. If context is empty, it immediately returns a refusal message without making an LLM call. This completely eliminates hallucination risk for out-of-scope queries.

# Layer 2: In-Prompt Instructions

The system prompt explicitly instructs the model to answer ONLY from provided context, refuse when uncertain, never fabricate details, and avoid using external knowledge.

The prompt uses numbered context chunks, clear section separators, and explicit prohibitions to reinforce grounding.

# Layer 3: Post-Generation Validation

Current validation includes response length checks, empty response handling, and error message standardization. Future enhancements will add keyword relevance checking and confidence scoring.


  10.Refusal Strategy

# When SAGE Refuses

Empty Context: No relevant chunks retrieved leads to immediate refusal

Out-of-Scope: Topic not in knowledge base leads to polite refusal with guidance

Partial Information: Incomplete context leads to providing available info with caveats OR refusing

Ambiguous Query: Multiple interpretations leads to asking for clarification

Fabrication Risk: Specific details not in docs leads to refusing and directing to contact

# Standard Response

"I don't have that information in my knowledge base. Please contact the university administration or check the official website."

This message is honest about limitations, provides alternatives, and maintains a helpful tone.


  11.Testing

# Test Coverage

Text Cleaning: 4 tests for preprocessing logic

PDF Extraction: 3 tests for document parsing

Retrieval: 4 tests for vector search logic (mocked ChromaDB)

Generation: 20+ tests for hallucination prevention

# Critical Scenarios

Empty Context Refusal:
Query about hostel curfew with no context must refuse

Fabrication Prevention:
Query for phone number not in docs must NOT generate fake number

Out-of-Scope Refusal:
Query about hostel with only library context must refuse

Cross-Domain Prevention:
Query about hostel with library or office locations must refuse

# Running Tests

All tests: pytest tests/ -v
Generation tests: pytest tests/test_generator.py -v
Single test: pytest tests/test_generator.py::test_name -v
With coverage: pytest tests/ --cov=src --cov-report=html

Test Files: tests/
  12.Configuration

# Models

LLaMA 3.1 8B: 4-bit quantized, approximately 4GB memory, medium speed
DeepSeek 6.7B: 4-bit quantized, approximately 3.5GB memory, faster

Quantization reduces model size from 16GB to 4GB and increases speed 2-3x with minimal accuracy loss (95% vs 100%). This makes it practical for production RAG systems.

# Key Parameters

Retrieval:
TOP_K = 5 (chunks retrieved)
CHUNK_SIZE = 500 (characters)
CHUNK_OVERLAP = 100 (characters)

Generation:
MAX_TOKENS = 512 (response length)
TIMEOUT = 30 (seconds)
TEMPERATURE = 0.7 (sampling)

Embedding:
MODEL = "all-MiniLM-L6-v2"
DIMENSIONS = 384


  13.Performance

# Latency

Query Embedding: approximately 50ms
Vector Search: approximately 100ms
LLM Generation: 2-5s
Total: 2-5 seconds

This is acceptable for interactive chatbot usage.

# Scalability

Current: 10+ PDFs, approximately 300 chunks, single user CLI

Future Options:
API deployment for multi-user (Flask/FastAPI)
GPU acceleration for faster generation
Distributed vector store (Milvus/Qdrant)
Batch processing for embeddings


# Project Structure

SAGE/
├── .venv/
│
├── data/
│   ├── processed/
│   │   └── cleaned_text.txt
│   │
│   ├── raw/
│   │   ├── academics/                     # contains 20+ syllabus documents (not expanded)
│   │   ├── administrative_regulations.pdf
│   │   ├── admission_enrollment.pdf
│   │   ├── campus_facilities.pdf
│   │   ├── faculty_staff.pdf
│   │   ├── fees_scholarships.pdf
│   │   ├── placement_internships.pdf
│   │   ├── research_innovation.pdf
│   │   ├── sample.pdf
│   │   ├── student_life.pdf
│   │   └── tech_portals.pdf
│   │
│   └── vector_db/
│       ├── 2fb2e8f1-e2e5-41...
│       └── chroma.sqlite3
│
├── docs/
│   ├── architecture.md
│   └── roadmap.md
│
├── models/
│   └── README.md
│
├── src/
│   ├── app/
│   │   ├── _pycache_/
│   │   ├── _init_.py
│   │   └── app.py
│   │
│   ├── data_extraction/
│   │   ├── _pycache_/
│   │   ├── _init_.py
│   │   ├── extract_academics.py
│   │   ├── extract_admin.py
│   │   ├── extract_admission.py
│   │   ├── extract_base.py
│   │   ├── extract_facilities.py
│   │   ├── extract_faculty.py
│   │   ├── extract_fees.py
│   │   ├── extract_placement.py
│   │   ├── extract_research.py
│   │   ├── extract_student_life.py
│   │   ├── extract_tech_portals.py
│   │   └── run_extraction.py
│   │
│   ├── embeddings/
│   │   ├── _pycache_/
│   │   ├── _init_.py
│   │   ├── embedder.py
│   │   └── vector_store.py
│   │
│   ├── generation/
│   │   ├── _pycache_/
│   │   ├── _init_.py
│   │   └── generator.py
│   │
│   ├── pipeline/
│   │   ├── _pycache_/
│   │   ├── _init_.py
│   │   └── rag_graph.py
│   │
│   ├── retrieval/
│   │   ├── _pycache_/
│   │   ├── _init_.py
│   │   └── retriever.py
│   │
│   └── utils/
│       ├── _pycache_/
│       ├── _init_.py
│       ├── clean_text.py
│       ├── logger.py
│       └── config.py
│
├── tests/
│   ├── test_clean_text.py
│   ├── test_extraction.py
│   ├── test_generator.py
│   └── test_retriever.py
│
├── .gitignore
├── diagnostic_chroma.py
├── LICENSE
├── README.md
└── requirements.txt


 14.Future Enhancements

# Short-term
Confidence scores for answers
Source citations in responses
Multi-turn conversation memory

# Medium-term
User feedback mechanism
Fine-tuning on university data
Hybrid search (keyword + semantic)

# Long-term
Multi-modal support (tables, images)
Voice interface
Proactive suggestions


Maintained By: SAGE Development Team

