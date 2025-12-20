# SAGE Chatbot – System Architecture

## 1. Introduction

SAGE (Smart Academic Guidance Engine) is a Retrieval-Augmented Generation (RAG) based chatbot designed to answer university-related questions using only official and verified institutional documents.

The primary goal of SAGE is accuracy and trust. If the required information is not available in the documents, the system will refuse to answer instead of guessing or generating incorrect information.

---

## 2. High-Level System Flow

User Question
↓
Retriever (Vector Search)
↓
Relevant Document Chunks
↓
Generator (LLM with strict rules)
↓
Final Answer OR Safe Refusal

---

## 3. Project Structure Overview
SAGE/
├── data/
│ ├── raw/ # Original university PDFs
│ ├── processed/ # Cleaned merged text
│ └── vector_db/ # ChromaDB storage
│
├── src/
│ ├── data_extraction/ # PDF extraction logic
│ ├── embeddings/ # Text chunking & embeddings
│ ├── retrieval/ # Context retrieval
│ ├── generation/ # Answer generation
│ ├── pipeline/ # RAG flow controller
│ └── utils/ # Cleaning, config, logging
│
├── tests/ # Unit tests
└── docs/
└── architecture.md

---

## 4. Data Extraction Layer

### Purpose
Convert university PDFs into clean and structured text.

### Input
- Academics (syllabus PDFs)
- Admission & enrollment
- Fees & scholarships
- Facilities
- Faculty
- Placement
- Research
- Student life
- Regulations

### Process
1. Extract text using PyMuPDF
2. Remove noise and formatting issues
3. Normalize spacing and characters
4. Add clear section headers

### Output
data/processed/cleaned_text.txt

### Key Files
- `extract_base.py`
- `extract_academics.py`
- `extract_fees.py`
- `extract_facilities.py`
- `run_extraction.py`

---

## 5. Embedding & Vector Store Layer

### Purpose
Make document content searchable using semantic similarity.

### Process
1. Split cleaned text into small chunks
2. Convert each chunk into vector embeddings
3. Store embeddings in ChromaDB

### Technology
- Embedding model: all-MiniLM-L6-v2
- Vector database: ChromaDB (persistent)

### Key Files
- `embedder.py`
- `vector_store.py`

---

## 6. Retrieval Layer

### Purpose
Find the most relevant document chunks for a user query.

### Flow
1. Convert user query into an embedding
2. Perform similarity search in ChromaDB
3. Retrieve top-K relevant chunks

### Safety Rule
- If no relevant chunks are found, the system stops and refuses to answer

### Key File
- `retriever.py`

---

## 7. Generation Layer

### Purpose
Generate answers strictly from retrieved context.

### Model
- Primary: llama3.1:8b (Ollama)
- Fallback: DeepSeek

### Prompt Rules
1. Answer only from provided context
2. Do not use external knowledge
3. Do not guess or assume
4. Refuse if information is missing

### Prompt Structure
SYSTEM RULES

===== CONTEXT =====
Retrieved document chunks

===== QUESTION =====
User question

===== ANSWER =====

### Key File
- `generator.py`

---

## 8. RAG Pipeline

### Purpose
Connect retrieval and generation into a single flow.

### Steps
1. Accept user query
2. Retrieve relevant context
3. Validate context availability
4. Generate answer or refusal

### Key File
- `rag_graph.py`

---

## 9. Hallucination Prevention Strategy

### Protection Layers
- Retrieval-level filtering
- Strict system prompt rules
- Extensive unit testing

### Example
Query: "What is hostel curfew time?"
Context: Not available  
Result: Safe refusal

---

## 10. Testing Architecture

### Purpose
Ensure correctness, safety, and stability.

### Test Files
- `test_clean_text.py`
- `test_extraction.py`
- `test_retriever.py`
- `test_generator.py` (mocked LLM)

### Benefit
- No dependency on real LLM
- Fast and reliable testing
- CI friendly

---

## 11. Current Limitations

- No multi-turn memory
- Occasional over-refusal
- No citation display yet

---

## 12. Planned Improvements

- Chunk-level citation
- Confidence scoring
- Multi-turn conversation memory
- Metadata-based filtering

---

## 13. Why This Architecture Is Strong

- Zero hallucination tolerance
- Fully testable design
- Clear separation of responsibilities
- Easy to maintain and extend
- Mentor and academic friendly

---

14. Team Responsibilities & Project Ownership

The SAGE Chatbot project follows a clear division of responsibilities across the full development lifecycle to ensure modularity, reliability, and smooth integration. Each team member owns specific technical domains while collaborating at integration points.

Overall Role Distribution
Team Member	Primary Responsibility  |	Secondary Responsibility
Barani	Pipeline Integration, CLI/App Flow  |	Embeddings, end-to-end demo flow
Darineesh	Prompt Engineering, Usage & Safety  | 	LLM behavior control, refusal design
Mani	Architecture, Retrieval, Testing	 |  Data extraction support, quality validation
 
**Project:** SAGE Chatbot  

