# src/data_extraction/extract_placement.py

from src.data_extraction.extract_base import extract_from_pdf_fitz
from src.utils.clean_text import clean_text


def extract_placement(pdf_path: str) -> str:
    """
    Extract and clean text from placement_internship.pdf

    Contains:
    - Training & Placement Cell details
    - Placement officers and contacts
    - Recruiters list
    - Placement statistics
    - Internship rules and evaluation process
    """

    # Step 1: Base extraction (mechanics only)
    raw_text = extract_from_pdf_fitz(pdf_path)

    # Step 2: Standard cleaning
    cleaned = clean_text(raw_text)

    # Step 3: Mandatory SOURCE header (DO NOT CHANGE FORMAT)
    return f"""===== SOURCE: placement_internship =====
{cleaned}
"""


# 🔹 TEMP LOCAL TEST (REMOVE BEFORE COMMIT)
if __name__ == "__main__":
    pdf_path = "data/raw/placement_internship.pdf"
    text = extract_placement(pdf_path)
    print(text[:1000])   # print first 1000 characters
