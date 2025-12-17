# src/data_extraction/extract_fees.py

from src.data_extraction.extract_base import extract_from_pdf_fitz
from src.utils.clean_text import clean_text


def extract_fees(pdf_path: str) -> str:
    """
    Extract and clean text from fees_scholarships.pdf
    
    This PDF contains TWO major sections:
    
    PART 1 - SCHOLARSHIPS:
    - National Scholarship Portal (NSP) information and OTR registration
    - Common Service Centres (CSC) services
    - Aadhaar authentication troubleshooting
    - Application process and requirements
    - Puducherry UT Government scholarships (SC/ST/OBC schemes)
    - Central Government scholarships (various merit and need-based)
    - State-specific scholarships (Tripura, Uttarakhand, Meghalaya, etc.)
    - UGC scholarships (Ishan Uday, PG studies)
    - AICTE scholarships (Pragati, Swanath, Saksham)
    - Private scholarships (Reliance Foundation, Siemens, PTU Alumni)
    
    PART 2 - FEE STRUCTURE:
    - B.Tech fee structure (Government quota, Self-supporting, NRI, CIWGC, JoSAA)
    - Different categories (General, SC/ST, OBC, EWS)
    - PKIET Karaikal fee structure (Puducherry and Other State residents)
    - Women's Engineering College (WEC) fees
    - Private engineering colleges fees
    - Hostel fees and bus pass fees
    - M.Tech/MCA/M.Sc fee structure
    - Ph.D fee structure and admissions
    - Visvesvaraya Ph.D Scheme fellowship details
    - Refund policies
    
    Args:
        pdf_path: Path to the fees_scholarships.pdf file
        
    Returns:
        Cleaned text with source header
    """
    # Step 1: Extract raw text using base extractor
    raw_text = extract_from_pdf_fitz(pdf_path)
    
    # Step 2: Apply stronger cleaning
    cleaned = clean_text(raw_text)
    
    # Step 3: Return with proper source header
    return f"""===== SOURCE: fees_scholarships =====
{cleaned}
"""
