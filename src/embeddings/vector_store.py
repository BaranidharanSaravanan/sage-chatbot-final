# src/embeddings/vector_store.py

import os
import chromadb
from chromadb.utils import embedding_functions
from typing import List

from src.embeddings.embedder import load_cleaned_text, chunk_text, MiniLMEmbedder

# ---------- Paths ----------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
VECTOR_DB_PATH = os.path.join(BASE_DIR, "data", "vector_db")
CLEANED_TEXT_PATH = os.path.join(BASE_DIR, "data", "processed", "cleaned_text.txt")

os.makedirs(VECTOR_DB_PATH, exist_ok=True)

class ChromaVectorStore:
    def __init__(self, collection_name: str = "sage_docs"):
        self.client = chromadb.PersistentClient(path=VECTOR_DB_PATH)

        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="all-MiniLM-L6-v2"
            )
        )

    def add_documents(self, texts: List[str], batch_size: int = 5000):
        if not texts:
            print("❌ No texts to store")
            return

        for start in range(0, len(texts), batch_size):
            end = start + batch_size
            self.collection.add(
                documents=texts[start:end],
                ids=[f"chunk_{i}" for i in range(start, min(end, len(texts)))]
            )

    def count(self) -> int:
        return self.collection.count()


# ---------- Run ----------
if __name__ == "__main__":
    print("Loading cleaned text...")
    text = load_cleaned_text(CLEANED_TEXT_PATH)

    print("Chunking...")
    chunks = chunk_text(text)

    print("Storing in ChromaDB...")
    store = ChromaVectorStore()
    store.add_documents(chunks)

    print(f"✅ Stored {store.count()} chunks")
