# src/data_extraction/extract_tech.py

from src.data_extraction.extract_base import extract_from_pdf_fitz
from src.utils.clean_text import clean_text

def extract_tech(pdf_path: str) -> str:
    """
    Extract and clean text from tech_portals.pdf
    
    This PDF contains:
    - IIS (Institute Information System)
    - IEEE Student Branch information
    - COE (Controller of Examinations) procedures
    - Fee payment portals
    - Enrollment, feedback, course registration processes
    
    Args:
        pdf_path: Path to the tech_portals.pdf file
        
    Returns:
        Cleaned text with source header
    """
    # Step 1: Extract raw text using base extractor
    raw_text = extract_from_pdf_fitz(pdf_path)
    
    # Step 2: Apply stronger cleaning
    cleaned = clean_text(raw_text)
    
    # Step 3: Return with proper source header
    return f"""===== SOURCE: tech_portals =====
{cleaned}
"""