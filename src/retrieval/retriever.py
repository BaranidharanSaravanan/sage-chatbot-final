# src/retrieval/retriever.py

import os
from typing import List
import chromadb

from src.utils.logger import get_logger

logger = get_logger(__name__)

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
        self.min_score = min_score
        self.collection = None

        logger.info("Initializing Retriever")

        if not os.path.exists(VECTOR_DB_PATH):
            logger.warning("Vector DB path does not exist")
            return

        try:
            client = chromadb.PersistentClient(path=VECTOR_DB_PATH)
            self.collection = client.get_collection(name=COLLECTION_NAME)
            logger.info("ChromaDB collection loaded successfully")
        except Exception as e:
            logger.exception("Failed to load ChromaDB collection")
            self.collection = None

    def retrieve(self, query: str) -> List[str]:
        if not query or not query.strip():
            logger.warning("Empty query received")
            return []

        if self.collection is None:
            logger.warning("No vector collection available")
            return []

        try:
            logger.info(f"Querying vector DB | top_k={self.top_k}")

            results = self.collection.query(
                query_texts=[query],
                n_results=self.top_k,
                include=["documents", "distances"]
            )

            docs = results.get("documents", [[]])[0]
            scores = results.get("distances", [[]])[0]

            filtered_docs = [
                doc for doc, score in zip(docs, scores)
                if score >= self.min_score
            ]

            logger.info(
                f"Retrieved {len(filtered_docs)} relevant docs "
                f"(threshold={self.min_score})"
            )

            return filtered_docs

        except Exception:
            logger.exception("Error during retrieval")
            return []


# ---------- Local Test ----------
if __name__ == "__main__":
    r = Retriever(top_k=10, min_score=0.2)
    docs = r.retrieve("What clubs are present?")
    print("Retrieved:", len(docs))
