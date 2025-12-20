# SAGE Chatbot Architecture

> Smart Academic Guidance Engine - Technical Architecture Documentation

---

## Table of Contents

- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Core Components](#core-components)
- [Data Pipeline](#data-pipeline)
- [Prompt Engineering](#prompt-engineering)
- [Hallucination Prevention](#hallucination-prevention)
- [Testing Strategy](#testing-strategy)
- [Configuration](#configuration)
- [Performance](#performance)

---

## Overview

SAGE is a Retrieval-Augmented Generation chatbot that provides accurate, document-grounded answers to university-related queries. The system prioritizes factual accuracy through strict hallucination controls and context-grounded response generation.

### Key Design Goals

- **Accuracy First** - Zero tolerance for fabricated information
- **Context Grounded** - All answers derived from verified documents
- **Graceful Degradation** - Polite refusal when information unavailable
- **Modular Design** - Independently testable components
- **Multi-Model Support** - Configurable LLM backends

---

## System Architecture

### High-Level Flow

```
┌─────────────┐
│  User Query │
└──────┬──────┘
       │
       v
┌─────────────────┐
│   Retriever     │  Fetch relevant chunks from vector DB
│  (ChromaDB)     │  using semantic similarity search
└──────┬──────────┘
       │
       v
┌─────────────────┐
│   Generator     │  LLM generates grounded answer
│  (LLaMA 3.1)    │  using structured prompt
└──────┬──────────┘
       │
       v
┌─────────────────┐
│    Response     │  Factual answer OR polite refusal
└─────────────────┘
```

### Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Data Extraction** | PyMuPDF | PDF to text conversion |
| **Text Processing** | Custom rules | Cleaning and normalization |
| **Embeddings** | all-MiniLM-L6-v2 | Text to 384-dim vectors |
| **Vector Store** | ChromaDB | Persistent vector storage |
| **Retrieval** | Cosine similarity | Semantic search |
| **Generation** | LLaMA 3.1 8B | Answer generation |
| **Orchestration** | LangGraph | RAG pipeline management |
| **Interface** | CLI (colorama) | User interaction |

---

## Core Components

### 1. Data Extraction Layer

Converts PDF documents into clean, structured text suitable for embedding.

**Key Features:**
- Base extraction using PyMuPDF
- Document-specific cleaning rules
- Ligature normalization
- Header and footer removal
- Source attribution preserved

**Process Flow:**

```
PDF Document
    ↓
PyMuPDF extraction
    ↓
Basic cleaning (printable chars, ligatures)
    ↓
Document-specific rules
    ↓
Cleaned text with source markers
```

### 2. Embedding Layer

Transforms text into vector representations for semantic search.

**Configuration:**
- **Model**: all-MiniLM-L6-v2 (SentenceTransformers)
- **Dimensions**: 384
- **Chunk Size**: 500 characters
- **Overlap**: 100 characters

**Chunking Strategy:**

Overlapping windows maintain context across boundaries while keeping chunks manageable for the embedding model.

```
Text: "The library is open from 8 AM to 8 PM on weekdays..."

Chunk 1: [0:500]   "The library is open from..."
Chunk 2: [400:900] "...8 PM on weekdays. On weekends..."
                    ↑
                    100 char overlap
```

### 3. Vector Store

Persistent storage and similarity search using ChromaDB.

**Storage Structure:**

```
data/vector_db/
├── chroma.sqlite3          # Metadata and indices
└── [uuid-collections]/     # Vector embeddings
```

**Key Features:**
- Automatic embedding on insert
- Cosine similarity search
- Persistent SQLite backend
- Collection-based organization

### 4. Retrieval Layer

Finds the most relevant document chunks for a given query.

**Implementation:**

```python
class Retriever:
    def __init__(self, top_k: int = 5):
        self.client = chromadb.PersistentClient(path=VECTOR_DB_PATH)
        self.collection = self.client.get_collection(name="sage_docs")
        self.top_k = top_k
    
    def retrieve(self, query: str) -> List[str]:
        results = self.collection.query(
            query_texts=[query],
            n_results=self.top_k
        )
        return results["documents"][0] if results["documents"] else []
```

**Configuration:**
- Default top-k: 5 chunks
- Similarity metric: Cosine
- No re-ranking (future enhancement)

### 5. Generation Layer

Generates contextually grounded answers using a structured approach.

**Supported Models:**

| Model | Parameters | Memory | Speed | Use Case |
|-------|-----------|--------|-------|----------|
| LLaMA 3.1 8B | 8B | ~4 GB | Medium | Primary (best balance) |
| DeepSeek 6.7B | 6.7B | ~3.5 GB | Fast | Alternative (faster) |

**Key Features:**
- Three-section structured prompt
- Empty context immediate refusal
- Timeout handling (30 seconds)
- Error message formatting
- Context chunking with labels

### 6. RAG Pipeline

Orchestrates the retrieval and generation process using LangGraph.

**State Definition:**

```python
class RAGState(TypedDict):
    question: str       # User input query
    context: List[str]  # Retrieved document chunks
    answer: str         # Generated response
```

**Execution Graph:**

```
START
  ↓
retrieve_node (fetch top-k chunks)
  ↓
generate_node (create grounded answer)
  ↓
END
```

### 7. Application Layer

Command-line interface with colored output for user interaction.

**Features:**
- Interactive chat loop
- Colored formatting (questions in green, answers in magenta)
- Session history tracking
- Graceful exit commands

---

## Data Pipeline

### Offline Processing

Initial setup phase that prepares the knowledge base:

**Step 1: Extraction**
```
10 PDF files → PyMuPDF → Document-specific rules → cleaned_text.txt
```
Output: ~150 KB of cleaned text

**Step 2: Chunking**
```
cleaned_text.txt → 500-char chunks with 100-char overlap → ~300 chunks
```

**Step 3: Embedding**
```
300 text chunks → MiniLM encoder → 300 x 384-dim vectors
```

**Step 4: Storage**
```
Vectors + metadata → ChromaDB → Persistent storage
```

### Online Processing

Runtime query handling:

**Step 1: Query Embedding**
```
User query → MiniLM encoder → 384-dim query vector
```

**Step 2: Similarity Search**
```
Query vector → ChromaDB cosine similarity → Top-5 chunks
```

**Step 3: Answer Generation**
```
Query + 5 chunks → LLaMA with structured prompt → Grounded answer
```

**Step 4: Display**
```
Answer → CLI with formatting → User sees response
```

---

## Prompt Engineering

### System Prompt Architecture

The generator uses a carefully structured three-section prompt:

#### Section 1: Core Rules

Non-negotiable constraints that define system behavior:

1. Answer ONLY from provided Context
2. Refuse if Context lacks answer
3. No assumptions or inferences
4. No cross-context information mixing
5. Ask for clarification if ambiguous

#### Section 2: Response Guidelines

Quality standards for useful responses:

- Be concise and direct
- Cite specific details (timings, locations, procedures)
- Acknowledge partial information with caveats
- Maintain professional, helpful tone
- List procedural steps clearly

#### Section 3: Forbidden Behaviors

Explicit prohibitions to prevent hallucination:

- Never fabricate details (phone numbers, dates, names, procedures)
- Never answer out-of-scope queries
- Never use external knowledge or training data
- Never use uncertain language ("I think", "probably")

### Prompt Template Structure

```
{SYSTEM_PROMPT}

===== CONTEXT =====
[Chunk 1]
<retrieved context chunk 1>

[Chunk 2]
<retrieved context chunk 2>

[Chunk 3-5]
<additional context chunks>

===== USER QUESTION =====
<user's original query>

===== YOUR ANSWER =====
```

### Design Rationale

| Design Element | Purpose |
|---------------|---------|
| Numbered chunks | Enables potential source citation |
| Clear separators | Prevents context bleeding |
| Structured sections | Reduces model confusion |
| Explicit prohibitions | Reinforces boundaries with negative examples |

---

## Hallucination Prevention

### Three-Layer Defense System

#### Layer 1: Pre-Generation Filter

Prevents unnecessary LLM calls when information is unavailable:

```python
if not context or all(not c.strip() for c in context):
    return "I don't have that information in my knowledge base. 
            Please contact the university administration or 
            check the official website."
```

**Benefits:**
- Saves compute resources
- Faster refusal responses
- No chance of hallucination

#### Layer 2: In-Prompt Instructions

Structured prompt enforces grounding:

- **Explicit Training**: Model instructed to refuse gracefully
- **Repetition**: "ONLY from Context" repeated multiple times
- **Negative Examples**: Forbidden behaviors explicitly listed
- **Template Responses**: Pre-defined refusal messages

#### Layer 3: Post-Generation Validation

Quality checks on generated responses:

**Current Implementation:**
- Empty response detection
- Error handling (timeout, model failure)
- Response formatting validation

**Planned Enhancements:**
- Keyword relevance checking

Maintained By: SAGE Development Team


