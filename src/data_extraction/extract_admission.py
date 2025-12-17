from src.data_extraction.extract_base import extract_from_pdf_fitz
from src.utils.clean_text import clean_text

def extract_admission(pdf_path: str) -> str:
    """
    Extract admission and enrollment related information.
    """
    raw_text = extract_from_pdf_fitz(pdf_path)

    # Minimal PDF-specific handling
    # (Base extractor + clean_text already handle most noise)
    text = raw_text

    cleaned = clean_text(text)

    return f"""===== SOURCE: admission_enrollment =====
{cleaned}
"""


# 🔹 LOCAL TEST (REMOVE BEFORE COMMIT)
if __name__ == "__main__":
    text = extract_admission("data/raw/admission_enrollment.pdf")
    print(text[:1000])
