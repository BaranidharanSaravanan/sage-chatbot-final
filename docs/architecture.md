# SAGE Chatbot - Architecture & Prompt Engineering

## System Overview

SAGE (Smart Academic Guidance Engine) is a RAG-based chatbot designed to answer university-related queries using only verified institutional documents. The system prioritizes **factual accuracy** and **hallucination prevention** over conversational fluency.

---

## Architecture Components

```
User Query
    ↓
[Retriever] → Fetch top-K chunks from ChromaDB
    ↓
[Generator] → LLM generates answer from context ONLY
    ↓
Response (grounded or refusal)
```

### Component Responsibilities

| Component | Purpose | Key Files |
|-----------|---------|-----------|
| **Data Extraction** | Extract & clean text from PDFs | `src/data_extraction/` |
| **Embeddings** | Chunk text & create vector embeddings | `src/embeddings/` |
| **Vector Store** | Store & retrieve document chunks | ChromaDB (`data/vector_db/`) |
| **Retriever** | Fetch top-K relevant chunks for query | `src/retrieval/retriever.py` |
| **Generator** | Generate context-grounded answers | `src/generation/generator.py` |
| **RAG Pipeline** | Orchestrate retrieval → generation | `src/pipeline/rag_graph.py` |

---

## Prompt Engineering Strategy

### 1. Design Philosophy

**Primary Goal:** Zero hallucination tolerance  
**Secondary Goal:** Helpful, accurate responses  
**Trade-off:** Refuse to answer rather than fabricate

### 2. System Prompt Structure

The generator uses a structured system prompt with three sections:

#### **Section A: Core Rules** (Non-negotiable constraints)
```
1. Answer ONLY from provided Context
2. Refuse if Context lacks answer
3. No assumptions or inferences
4. No cross-context mixing (unless explicit)
5. Ask for clarification if ambiguous
```

**Rationale:** Establishes hard boundaries for the model's behavior.

#### **Section B: Response Guidelines** (Quality standards)
```
- Be concise and direct
- Cite specific details (timings, locations)
- Acknowledge partial information
- Professional, helpful tone
- Clear procedural steps
```

**Rationale:** Ensures responses are useful when they CAN be provided.

#### **Section C: Forbidden Behaviors** (Explicit prohibitions)
```
- Never fabricate details
- Never answer out-of-scope queries
- Never use external knowledge
- Never use uncertainty language ("I think", "probably")
```

**Rationale:** Reinforces hallucination prevention through negative examples.

### 3. Prompt Template Format

```
{SYSTEM_PROMPT}

===== CONTEXT =====
[Chunk 1]
<retrieved context 1>

[Chunk 2]
<retrieved context 2>
...

===== USER QUESTION =====
<user query>

===== YOUR ANSWER =====
```

**Design Decisions:**
- **Chunked Context:** Numbered chunks improve model's ability to cite sources
- **Clear Separators:** `=====` markers prevent context bleeding
- **Structured Flow:** System rules → Data → Query → Response reduces confusion

---

## Hallucination Prevention Mechanisms

### Layer 1: Pre-Generation (Retrieval)
- **Empty Context Check:** If retriever returns no chunks, immediate refusal
- **Relevance Threshold:** Low-confidence retrievals trigger refusal

### Layer 2: In-Prompt (System Instructions)
- **Explicit Refusal Training:** Model is instructed to refuse gracefully
- **Grounding Emphasis:** "ONLY from Context" repeated multiple times
- **Forbidden Behaviors:** Explicitly lists what NOT to do

### Layer 3: Post-Generation (Validation - Future Work)
- Answer length sanity check (not empty)
- Keyword matching (ensure answer relates to query)
- Confidence scoring (if model provides it)

---

## Refusal Strategy

### When to Refuse

| Scenario | Example | Action |
|----------|---------|--------|
| **Empty Context** | No chunks retrieved | Refuse immediately |
| **Out-of-Scope** | Query about unrelated topic | Refuse with guidance |
| **Partial Info** | Context has 50% of answer | Either partial answer + caveat OR full refusal |
| **Ambiguous Query** | "When does it open?" (what?) | Ask for clarification |
| **Fabrication Risk** | Asking for phone numbers not in context | Refuse + suggest contact method |

### Refusal Message Template

**Standard Refusal:**
```
"I don't have that information in my knowledge base. 
Please contact the university administration or check the official website."
```

**Why This Phrasing:**
- ✅ Honest about limitation
- ✅ Provides alternative action
- ✅ Maintains helpful tone
- ❌ Doesn't apologize excessively
- ❌ Doesn't make excuses

---

## Edge Case Handling

### 1. Ambiguous Queries
**Example:** "What are the hours?"  
**Strategy:** 
- If context has multiple "hours" (library, gym, office) → list all
- If context unclear → ask "Do you mean library hours, gym hours, or office hours?"

### 2. Compound Questions
**Example:** "What are the library hours and admission fees?"  
**Strategy:**
- Answer both if context contains both
- If partial: "Library hours are X. I don't have fee information."

### 3. Leading Questions
**Example:** "The hostel curfew is 10 PM, right?"  
**Strategy:**
- If context confirms → confirm
- If context conflicts → correct with context info
- If context silent → refuse, don't confirm assumption

### 4. Temporal Queries
**Example:** "Is the library open right now?"  
**Strategy:**
- Provide hours from context
- Do NOT infer current day/time
- Response: "The library is open 8 AM - 8 PM on weekdays. You can check if it's currently within these hours."

---

## Model Configuration

### Supported Models

| Model | Size | Use Case |
|-------|------|----------|
| `llama3.1:8b` | 8B params (quantized) | Primary - Best balance |
| `deepseek-coder:6.7b` | 6.7B params | Alternative - Faster |

### Model Selection Strategy
- **Default:** LLaMA 3.1 8B (best instruction-following)
- **Fallback:** DeepSeek (if LLaMA unavailable)
- **Future:** Allow user selection via CLI

### Quantization Trade-offs
- ✅ Faster inference
- ✅ Lower memory usage
- ⚠️ Slightly reduced accuracy (acceptable for retrieval-augmented tasks)

---

## Testing Strategy

### Test Categories

1. **Normal Operations**
   - Correct answer with full context
   - Specific detail extraction
   - List-based queries

2. **Hallucination Prevention**
   - Empty context refusal
   - Out-of-scope query refusal
   - Fabrication prevention
   - Partial context handling

3. **Edge Cases**
   - Ambiguous queries
   - Whitespace-only context
   - Very long context
   - Special characters

4. **Error Handling**
   - None/null inputs
   - Invalid model names
   - Timeout scenarios

5. **Safety & Quality**
   - No external knowledge leakage
   - Consistent refusal format
   - Professional tone maintenance

### Critical Test Scenarios

**Scenario: Fabrication of Contact Details**
```python
Query: "What is the admissions office phone number?"
Context: [Admission process, dates, documents] (NO PHONE NUMBER)
Expected: REFUSE - must not generate +91-XXXXXXXXXX
```

**Scenario: Temporal Inference Prevention**
```python
Query: "Can I visit the library today?"
Context: [Library hours: Mon-Fri 8AM-8PM]
Expected: Provide hours, do NOT say "yes" or "no" (can't know today's date)
```

**Scenario: Cross-Domain Confusion**
```python
Query: "Where is the hostel?"
Context: [Library location, admission office location]
Expected: REFUSE - completely different domain
```

---

## Prompt Evolution History

### Version 1 (Initial - Day 1)
```
"You are a helpful assistant. Answer the question using the context."
```
**Issues:** Too permissive, frequent hallucinations

### Version 2 (Day 2)
```
"Answer using ONLY the context. If not in context, say you cannot answer."
```
**Issues:** Still generated plausible-sounding wrong answers

### Version 3 (Day 3 - Current)
```
CORE RULES + RESPONSE GUIDELINES + FORBIDDEN BEHAVIORS
```
**Improvements:**
- Explicit prohibition list
- Structured rules hierarchy
- Refusal message template
- Chunked context labeling

---

## Future Improvements

### Short-term (Week 1-2)
- [ ] Add confidence scoring to responses
- [ ] Implement citation of specific chunks
- [ ] Multi-turn conversation context

### Medium-term (Month 1)
- [ ] Fine-tune model on university-specific refusal patterns
- [ ] Add user feedback loop (thumbs up/down)
- [ ] Implement query reformulation for failed retrievals

### Long-term (Month 2+)
- [ ] Multi-modal support (answer from images in PDFs)
- [ ] Personalization (student vs. faculty responses)
- [ ] Proactive suggestions ("You might also want to know...")

---

## Collaboration Notes

### Handoff to Barani (Integration)
- System prompt is finalized in `Generator.SYSTEM_PROMPT`
- No configuration changes needed
- Prompt is model-agnostic (works with LLaMA & DeepSeek)

### Handoff to Mani (Testing)
- Test suite covers all edge cases in `tests/test_generator.py`
- Run with: `pytest tests/test_generator.py -v`
- Hallucination scenarios documented in test file

---

## References

- **LangGraph Docs:** https://langchain-ai.github.io/langgraph/
- **Prompt Engineering Guide:** https://www.promptingguide.ai/
- **RAG Best Practices:** [Internal team wiki]

---

**Document Owner:** Darineesh  
**Last Updated:** Day 3  
**Status:** ✅ Finalized for Integration
