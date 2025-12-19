# src/data_extraction/extract_student_life.py

from pathlib import Path
from src.data_extraction.extract_base import extract_from_pdf_fitz

def extract_student_life() -> str:
    """
    Extract text from student_life.pdf only.
    Uses shared base extractor.
    """

    pdf_path = Path("data/raw/student_life.pdf")

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    text = extract_from_pdf_fitz(str(pdf_path))
    return text


# 🔹 LOCAL TEST (RUN THIS FILE ONLY)
if __name__ == "__main__":
    content = extract_student_life()

    print("===== STUDENT LIFE PDF EXTRACTED TEXT (PREVIEW) =====")
    print(content[:3000])   # preview first 3000 chars
