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

Claude is AI and can make mistakes. Please double-check responses.
