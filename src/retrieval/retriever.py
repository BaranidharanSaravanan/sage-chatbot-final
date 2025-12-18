# src/retrieval/retriever.py

import os
import chromadb
from typing import List

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
VECTOR_DB_PATH = os.path.join(BASE_DIR, "data", "vector_db")

class Retriever:
    def __init__(self, top_k: int = 5):
        self.top_k = top_k
        self.client = chromadb.PersistentClient(path=VECTOR_DB_PATH)
        self.collection = self.client.get_collection(name="sage_docs")

    def retrieve(self, query: str) -> List[str]:
        results = self.collection.query(
            query_texts=[query],
            n_results=self.top_k
        )
        return results["documents"][0] if results["documents"] else []


if __name__ == "__main__":
    r = Retriever()
    docs = r.retrieve("What clubs are present?")
    print("Retrieved:", len(docs))
