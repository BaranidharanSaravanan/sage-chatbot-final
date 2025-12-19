# src/data_extraction/extract_student_life.py

from pathlib import Path
from src.data_extraction.extract_base import extract_from_pdf_fitz

def extract_student_life(pdf_path: str) -> str:
    """
    Extract text from student_life.pdf.
    
    Args:
        pdf_path (str): Path to the PDF file
    
    Returns:
        str: Extracted text
    """
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {path}")
    
    text = extract_from_pdf_fitz(str(path))
    return text

# 🔹 LOCAL TEST
if __name__ == "__main__":
    content = extract_student_life("data/raw/student_life.pdf")
    print(content[:3000])
