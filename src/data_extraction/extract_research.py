# src/data_extraction/extract_research.py

from src.data_extraction.extract_base import extract_from_pdf_fitz
from src.utils.clean_text import clean_text

def extract_research(pdf_path: str) -> str:
    """
    Extract and clean text from research_innovation.pdf
    
    This PDF contains:
    - AIC-PECF (Atal Incubation Centre)
    - IIC (Institution's Innovation Council)
    - Startup ecosystem and incubation support
    - Research submission processes
    - Publication and patent norms
    - Funding opportunities
    - National Innovation Policy
    
    Args:
        pdf_path: Path to the research_innovation.pdf file
        
    Returns:
        Cleaned text with source header
    """
    # Step 1: Extract raw text using base extractor
    raw_text = extract_from_pdf_fitz(pdf_path)
    
    # Step 2: Apply stronger cleaning
    cleaned = clean_text(raw_text)
    
    # Step 3: Return with proper source header
    return f"""===== SOURCE: research_innovation =====
{cleaned}
"""
