from src.data_extraction.extract_base import extract_from_pdf_fitz
from src.utils.clean_text import clean_text

def extract_facilities(pdf_path: str) -> str:
    """
    Extract campus facilities information such as
    hostels, medical, sports, library, clubs, etc.
    """
    raw_text = extract_from_pdf_fitz(pdf_path)

    # Facilities PDF has tables and lists — keep them as text
    text = raw_text

    cleaned = clean_text(text)

    return f"""===== SOURCE: campus_facilities =====
{cleaned}
"""


# 🔹 LOCAL TEST (REMOVE BEFORE COMMIT)
if __name__ == "__main__":
    text = extract_facilities("data/raw/campus_facilities.pdf")
    print(text[:1000])
