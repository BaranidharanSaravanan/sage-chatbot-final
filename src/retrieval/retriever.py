# src/retrieval/retriever.py

import os
from typing import List
import chromadb

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
VECTOR_DB_PATH = os.path.join(BASE_DIR, "data", "vector_db")
COLLECTION_NAME = "sage_docs"


class Retriever:
    """
    Retriever for SAGE Chatbot.

    Features:
    - top_k results
    - relevance threshold check to avoid hallucination
    """
    def __init__(self, top_k: int = 10, min_score: float = 0.2):
        self.top_k = top_k
        self.min_score = min_score  # minimum similarity to consider result
        self.collection = None

        if not os.path.exists(VECTOR_DB_PATH):
            return  # Vector DB not created yet

        try:
            client = chromadb.PersistentClient(path=VECTOR_DB_PATH)
            self.collection = client.get_collection(name=COLLECTION_NAME)
        except Exception:
            self.collection = None  # Missing or corrupted collection

    def retrieve(self, query: str) -> List[str]:
        if not query or not query.strip():
            return []

        if self.collection is None:
            return []

        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=self.top_k,
                include=["documents", "distances"]  # get similarity scores
            )

            docs = results.get("documents", [[]])[0]
            scores = results.get("distances", [[]])[0]

            # Only include docs above relevance threshold
            filtered_docs = [
                doc for doc, score in zip(docs, scores)
                if score >= self.min_score
            ]

            return filtered_docs

        except Exception:
            return []


# ---------- Local Test ----------
if __name__ == "__main__":
    r = Retriever(top_k=10, min_score=0.2)
    docs = r.retrieve("What clubs are present?")
    print("Retrieved:", len(docs))
