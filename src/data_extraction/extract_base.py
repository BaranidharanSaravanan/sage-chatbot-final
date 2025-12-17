import fitz  # PyMuPDF
from ..utils.clean_text import clean_text_basic


def extract_from_pdf_fitz(pdf_path: str) -> str:
    """
    Base PDF extractor.
    Responsibilities:
    - Open PDF using PyMuPDF
    - Loop through pages
    - Extract text
    - Apply basic cleaning
    - Skip empty pages
    Returns combined page text.
    """
    pages = []

    doc = fitz.open(pdf_path)
    for page in doc:
        text = page.get_text()
        text = clean_text_basic(text)

        if text.strip():  # skip empty pages
            pages.append(text)

    doc.close()
    return "\n".join(pages)


# 🔹 LOCAL TEST (REMOVE BEFORE COMMIT)
if __name__ == "__main__":
    test_pdf = "data/raw/sample.pdf"
    extracted = extract_from_pdf_fitz(test_pdf)
    print(extracted[:1000])
