# src/embeddings/embedder.py

from sentence_transformers import SentenceTransformer
from typing import List
import os


# ---------- Path Resolution ----------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
CLEANED_TEXT_PATH = os.path.join(
    BASE_DIR, "data", "processed", "cleaned_text.txt"
)


# ---------- Chunking ----------
def chunk_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 100
) -> List[str]:
    """
    Splits text into overlapping character-based chunks.
    """
    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start = end - overlap

    return chunks


# ---------- Load Text ----------
def load_cleaned_text(file_path: str) -> str:
    """
    Loads cleaned text from disk.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Cleaned text not found at: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


# ---------- Embeddings ----------
class MiniLMEmbedder:
    """
    Wrapper around MiniLM sentence transformer.
    """
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def embed(self, texts: List[str]):
        if not texts:
            return []

        return self.model.encode(
            texts,
            show_progress_bar=True,
            convert_to_numpy=True
        )


# ---------- Local Test ----------
if __name__ == "__main__":
    print("Loading cleaned text...")
    text = load_cleaned_text(CLEANED_TEXT_PATH)

    print("Chunking text...")
    chunks = chunk_text(text)

    print(f"Total chunks created: {len(chunks)}")

    if not chunks:
        print("⚠️ No chunks created (cleaned_text.txt may be empty)")
    else:
        embedder = MiniLMEmbedder()
        embeddings = embedder.embed(chunks)

        print("Embedding complete")
        print(f"Embedding shape: {embeddings.shape}")
        print("\nSample chunk:\n")
        print(chunks[0][:300])
