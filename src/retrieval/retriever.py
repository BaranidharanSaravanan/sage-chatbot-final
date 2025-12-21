# src/retrieval/retriever.py

import os
from typing import List
import chromadb

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
VECTOR_DB_PATH = os.path.join(BASE_DIR, "data", "vector_db")
COLLECTION_NAME = "sage_docs"


class Retriever:
    def __init__(self, top_k: int = 10):
        self.top_k = top_k
        self.collection = None

        if not os.path.exists(VECTOR_DB_PATH):
            # Vector DB not created yet – allowed
            return

        try:
            client = chromadb.PersistentClient(path=VECTOR_DB_PATH)
            self.collection = client.get_collection(name=COLLECTION_NAME)
        except Exception:
            # Collection missing or corrupted – fail silently
            self.collection = None

    def retrieve(self, query: str) -> List[str]:
        if not query or not query.strip():
            return []

        if self.collection is None:
            return []

        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=self.top_k
            )
            return results.get("documents", [[]])[0]
        except Exception:
            return []


if __name__ == "__main__":
    r = Retriever()
    docs = r.retrieve("What clubs are present?")
    print("Retrieved:", len(docs))
