import os
from src.data_extraction.extract_base import extract_from_pdf_fitz
from src.utils.clean_text import clean_text

ACADEMICS_DIR = "data/raw/academics"

ACADEMIC_FILES = [
    # UG – B.Tech
    ("UG B.Tech", "Common First Year", "ug_btech_common_first_year.pdf"),
    ("UG B.Tech", "Chemical Engineering", "ug_btech_chemical.pdf"),
    ("UG B.Tech", "Civil Engineering", "ug_btech_civil.pdf"),
    ("UG B.Tech", "Computer Science and Engineering", "ug_btech_cse.pdf"),
    ("UG B.Tech", "Electrical and Electronics Engineering", "ug_btech_eee.pdf"),
    ("UG B.Tech", "Electronics and Communication Engineering", "ug_btech_ece.pdf"),
    ("UG B.Tech", "Electronics and Instrumentation Engineering", "ug_btech_eie.pdf"),
    ("UG B.Tech", "Information Technology", "ug_btech_it.pdf"),
    ("UG B.Tech", "Mechanical Engineering", "ug_btech_me.pdf"),
    ("UG B.Tech", "Mechatronics Engineering", "ug_btech_mt.pdf"),

    # PG – M.Tech
    ("PG M.Tech", "CE – Environmental Engineering", "pg_mtech_ce_environmental.pdf"),
    ("PG M.Tech", "CE – Structural Engineering", "pg_mtech_ce_structural.pdf"),
    ("PG M.Tech", "CSE – Information Security", "pg_mtech_cse_infosec.pdf"),
    ("PG M.Tech", "CSE – Data Science", "pg_mtech_cse_datascience.pdf"),
    ("PG M.Tech", "EEE – Electrical Drives and Control", "pg_mtech_eee_drives.pdf"),
    ("PG M.Tech", "ECE – Electronics and Communication", "pg_mtech_ece_ece.pdf"),
    ("PG M.Tech", "ECE – Wireless Communication", "pg_mtech_ece_wireless.pdf"),
    ("PG M.Tech", "EIE – Instrumentation Engineering", "pg_mtech_eie_instrumentation.pdf"),
    ("PG M.Tech", "IT – Internet of Things", "pg_mtech_it_iot.pdf"),
    ("PG M.Tech", "ME – Energy Technology", "pg_mtech_me_energy.pdf"),
    ("PG M.Tech", "ME – Product Design and Manufacturing", "pg_mtech_me_pdm.pdf"),
    ("PG M.Tech", "Chemical Engineering", "pg_mtech_chemical.pdf"),

    # Other PG
    ("PG MBA", "Innovation, Entrepreneurship & Venture Development", "mba_ievd.pdf"),
    ("PG MBA", "International Business", "mba_ib.pdf"),
    ("PG MCA", "Computer Applications", "mca.pdf"),
    ("PG MSc", "Science", "msc.pdf"),
]


def extract_academics(_: str = "") -> str:
    """
    Extract and merge all academic curriculum PDFs into one structured output.
    """
    sections = []

    for program, department, filename in ACADEMIC_FILES:
        pdf_path = os.path.join(ACADEMICS_DIR, filename)

        if not os.path.exists(pdf_path):
            continue  # silently skip missing files

        raw_text = extract_from_pdf_fitz(pdf_path)
        cleaned = clean_text(raw_text)

        if not cleaned.strip():
            continue

        section = f"""
===== PROGRAM: {program} =====
===== DEPARTMENT: {department} =====
===== SOURCE FILE: {filename.replace('.pdf','')} =====
{cleaned}
"""
        sections.append(section.strip())

    return "\n\n".join(sections)
