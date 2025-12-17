# src/data_extraction/extract_fees.py

from src.data_extraction.extract_base import extract_from_pdf_fitz
from src.utils.clean_text import clean_text

def extract_fees(pdf_path: str) -> str:
    """
    Extract and clean text from fees_scholarships.pdf
    
    This PDF contains:
    - National Scholarship Portal (NSP) information
    - OTR registration process
    - Puducherry UT Government scholarships
    - Central Government scholarships
    - UGC scholarships
    - AICTE scholarships
    - Private scholarships
    - Internship regulations and evaluation process
    
    Args:
        pdf_path: Path to the fees_scholarships.pdf file
        
    Returns:
        Cleaned text with source header
    """
    # Step 1: Extract raw text using base extractor
    # (already includes basic cleaning via clean_text_basic)
    raw_text = extract_from_pdf_fitz(pdf_path)
    
    # Step 2: Apply stronger cleaning
    # (removes extra whitespace, fixes line breaks, etc.)
    cleaned = clean_text(raw_text)
    
    # Step 3: Return with proper source header
    # IMPORTANT: Header format must be EXACT as specified
    return f"""===== SOURCE: fees_scholarships =====
{cleaned}
"""