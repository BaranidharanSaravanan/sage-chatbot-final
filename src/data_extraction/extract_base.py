# src/data_extraction/extract_base.py

import os
import fitz  # PyMuPDF
from utils.clean_text import clean_text

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text from a single PDF and return cleaned text.
    Steps:
    1. Open PDF using PyMuPDF
    2. Loop through pages
    3. Extract raw text
    4. Clean text using clean_text()
    5. Skip empty pages
    """
    cleaned_pages = []
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"Error opening {pdf_path}: {e}")
        return ""

    for page_num, page in enumerate(doc, start=1):
        try:
            raw_text = page.get_text()
            text = clean_text(raw_text)
            if text:  # skip empty pages
                cleaned_pages.append(text)
        except Exception as e:
            print(f"Error reading page {page_num} of {pdf_path}: {e}")
    
    doc.close()
    return "\n".join(cleaned_pages)


def extract_from_folder(folder_path: str) -> dict:
    """
    Loop through all PDFs in a folder and return a dictionary:
    {filename: cleaned_text}
    """
    results = {}
    if not os.path.exists(folder_path):
        print(f"Folder {folder_path} does not exist!")
        return results

    for filename in os.listdir(folder_path):
        if filename.lower().endswith(".pdf"):
            full_path = os.path.join(folder_path, filename)
            cleaned_text = extract_text_from_pdf(full_path)
            results[filename] = cleaned_text

    return results


# Quick test when running directly
if __name__ == "__main__":
    folder = "data/raw"
    extracted = extract_from_folder(folder)
    for fname, text in extracted.items():
        print(f"\n--- {fname} ---")
        print(text[:500], "...")  # print first 500 chars
