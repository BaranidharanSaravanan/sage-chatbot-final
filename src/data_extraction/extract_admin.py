import os
from src.data_extraction.extract_base import extract_from_pdf_fitz
from src.utils.clean_text import clean_text

ADMIN_REGULATIONS_DIR = "data/raw/administrative_regulations"

ADMIN_REGULATION_FILES = [
    ("PhD", "Regulations 2021", "PhD_Regulations_2021.pdf"),
    ("MBA", "Innovation, Entrepreneurship & Venture Development - Regulations 2021", "MBA_IEVD_Regulations_2021.pdf"),
    ("MBA", "International Business - Regulations 2021-22", "24 May 2023_ MBA_IB_Regulations_2122.pdf"),
    ("M.Sc", "Materials Science & Technology - Regulations 2019-20", "MSc_Regulations_1920.pdf"),
    ("MCA", "Computer Applications - Regulations 2021", "MCA_Regulations_2021.pdf"),
    ("M.Tech", "All Specializations - Regulations 2021", "24 may 2023_PTU_MTech_Regulations_2021.pdf"),
    ("B.Tech", "Constituent & Affiliated Colleges - Regulations 2022-23", "BTech_Regulations_ConstAffl_2022-23.pdf"),
    ("B.Tech", "NEP Regulations 2024-25", "PTU NEP Regulations 2024_25_ACM approved.pdf"),
]

def extract_regulations(_: str = "") -> dict:
    """
    Extract all administrative regulation PDFs and store raw and cleaned text.
    Returns a dictionary with filename as key and a dict containing raw and cleaned text.
    """
    all_texts = {}

    for program, regulation_type, filename in ADMIN_REGULATION_FILES:
        pdf_path = os.path.join(ADMIN_REGULATIONS_DIR, filename)
        if not os.path.exists(pdf_path):
            continue  # skip missing files

        raw_text = extract_from_pdf_fitz(pdf_path)
        cleaned = clean_text(raw_text)

        all_texts[filename] = {
            "program": program,
            "regulation_type": regulation_type,
            "raw_text": raw_text,
            "cleaned": cleaned
        }

    return all_texts
