Usage & Safety
Usage
Running the system:

python src/data_extraction/run_extraction.py - Extracts and cleans all PDFs
python src/embeddings/embedder.py - Creates text chunks from cleaned_text.txt
python src/embeddings/vector_store.py - Stores chunks in ChromaDB
python src/app/app.py - Run chatbot (type 'exit' or 'quit' to stop, Ctrl+C also works)

Text cleaning:

Removes non-printable characters
Fixes PDF ligatures (ﬁ→fi, ﬂ→fl, etc.)
Removes hyphenation at line breaks
Collapses multiple spaces

Chunking:

500 characters per chunk
100 character overlap between chunks
Uses all-MiniLM-L6-v2 model for embeddings

Safety
Refusal on empty/bad context:

Returns "I don't have that information in my knowledge base..." if context is empty or None

Error handling:

30 second timeout on Ollama calls
Catches FileNotFoundError if Ollama not installed
Catches subprocess errors and shows error messages
Handles empty model responses

System prompt rules:

Only answer from provided context
Never fabricate details
If context doesn't have the answer, refuse
Don't use external knowledge

Tests verify:

Refuses when context is empty
Refuses when context doesn't match question
Doesn't make up phone numbers or dates
Handles None context without crashing

Demo Instructions (Step-by-Step Flow)

This demo demonstrates how SAGE performs grounded question answering using a Retrieval-Augmented Generation (RAG) pipeline with selectable local LLMs.

1. Start the Chatbot

Run the CLI application:
python src/app/app.py

2. Model Selection (At Conversation Start)

On startup, SAGE prompts the user to select a language model.
Available models are listed (from config.py).
If no input is given, the default model is selected automatically.
The chosen model remains active for the entire conversation.

This ensures:
Explicit user control over model choice
Safe fallback behavior if input is invalid

3. Ask Questions

Enter natural-language questions related to university information.
Type exit or quit to end the session.

Example:
You: What are the library working hours?
SAGE: The university library is open from 8 AM to 8 PM on weekdays.

4. Internal Demo Flow (What Happens Behind the Scenes)

For every user question:

Retriever
Converts the query into embeddings
Searches ChromaDB for the top-k relevant chunks

Generator
Receives the retrieved text as context
Uses a strictly constrained system prompt
Generates an answer only from retrieved content

Safety Enforcement
If no relevant context is found, SAGE refuses to answer
No hallucination or external knowledge usage is allowed

5. Expected Demo Outcomes

Correct answers when information exists in the knowledge base
Safe refusal when information is missing or ambiguous
Consistent behavior across different supported models