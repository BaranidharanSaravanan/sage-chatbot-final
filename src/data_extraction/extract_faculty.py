# src/data_extraction/extract_faculty.py

from src.data_extraction.extract_base import extract_from_pdf_fitz
from src.utils.clean_text import clean_text


def extract_faculty(pdf_path: str) -> str:
    """
    Extract and clean text from faculty_staff.pdf
    """

    raw_text = extract_from_pdf_fitz(pdf_path)
    cleaned = clean_text(raw_text)

    return f"""===== SOURCE: faculty_staff =====
{cleaned}
"""


# 🔹 TEMP LOCAL TEST (REMOVE BEFORE COMMIT)
if __name__ == "__main__":
    pdf_path = "data/raw/faculty_staff.pdf"
    text = extract_faculty(pdf_path)
    print(text[:1000])

