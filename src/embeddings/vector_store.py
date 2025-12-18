# src/embeddings/vector_store.py

import os
import chromadb
from chromadb.config import Settings
from typing import List


# ---------- Paths ----------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
VECTOR_DB_PATH = os.path.join(BASE_DIR, "data", "vector_db")


# ---------- Vector Store ----------
class ChromaVectorStore:
    def __init__(self, collection_name: str = "sage_docs"):
        self.client = chromadb.Client(
            Settings(
                persist_directory=VECTOR_DB_PATH,
                anonymized_telemetry=False
            )
        )

        self.collection = self.client.get_or_create_collection(
            name=collection_name
        )

    def add_documents(
        self,
        texts: List[str],
        embeddings,
        source: str = "cleaned_text"
    ):
        if not texts:
            print("⚠️ No texts provided to store")
            return

        ids = [f"chunk_{i}" for i in range(len(texts))]
        metadatas = [
            {"chunk_id": i, "source": source}
            for i in range(len(texts))
        ]

        self.collection.add(
            documents=texts,
            embeddings=embeddings.tolist(),
            metadatas=metadatas,
            ids=ids
        )

        self.client.persist()

    def count(self) -> int:
        return self.collection.count()


# ---------- Local Test ----------
if __name__ == "__main__":
    from embedder import (
        load_cleaned_text,
        chunk_text,
        MiniLMEmbedder,
        CLEANED_TEXT_PATH
    )

    print("Loading text...")
    text = load_cleaned_text(CLEANED_TEXT_PATH)

    print("Chunking...")
    chunks = chunk_text(text)

    if not chunks:
        print("⚠️ No chunks to store. Exiting.")
        exit(0)

    print("Embedding...")
    embedder = MiniLMEmbedder()
    embeddings = embedder.embed(chunks)

    print("Storing in ChromaDB...")
    store = ChromaVectorStore()
    store.add_documents(chunks, embeddings)

    print(f"✅ Stored {store.count()} chunks in ChromaDB")
