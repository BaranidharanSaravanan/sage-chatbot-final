import os

# Barani
from src.data_extraction.extract_admission import extract_admission
from src.data_extraction.extract_facilities import extract_facilities
from src.data_extraction.extract_academics import extract_academics

# Darineesh
from src.data_extraction.extract_fees import extract_fees
from src.data_extraction.extract_tech_portals import extract_tech
from src.data_extraction.extract_research import extract_research

# Mani
from src.data_extraction.extract_placement import extract_placement
from src.data_extraction.extract_faculty import extract_faculty

# Vetri
from src.data_extraction.extract_student_life import extract_student_life
from src.data_extraction.extract_admin import extract_admin


OUTPUT_PATH = "data/processed/cleaned_text.txt"


def run_all_extractions() -> None:
    """
    Orchestrates all extractors and writes a single merged cleaned_text.txt
    """
    outputs = []

    # --- Barani ---
    outputs.append(extract_admission("data/raw/admission_enrollment.pdf"))
    outputs.append(extract_facilities("data/raw/campus_facilities.pdf"))
    outputs.append(extract_academics("data/raw/academics"))

    # --- Darineesh ---
    outputs.append(extract_fees("data/raw/fees_scholarships.pdf"))
    outputs.append(extract_tech("data/raw/tech_portals.pdf"))
    outputs.append(extract_research("data/raw/research_innovation.pdf"))

    # --- Mani ---
    outputs.append(extract_placement("data/raw/placement_internship.pdf"))
    outputs.append(extract_faculty("data/raw/faculty_staff.pdf"))

    # --- Vetri ---
    outputs.append(extract_student_life("data/raw/student_life.pdf"))
    outputs.append(extract_admin("data/raw/administration_regulations.pdf"))

    # Ensure output directory exists
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    # Write once
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        for block in outputs:
            if block and block.strip():
                f.write(block)
                f.write("\n\n")

    print("✅ Extraction complete → data/processed/cleaned_text.txt")


if __name__ == "__main__":
    run_all_extractions()
