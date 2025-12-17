# src/data_extraction/run_extraction.py

import os
from src.data_extraction.extract_base import extract_from_folder


def run_extraction(raw_folder: str, processed_folder: str, output_file: str = "cleaned_text.txt"):
    """
    Orchestrator function to extract text from PDFs and write to a single file.

    Steps:
    1. Extract text from all PDFs in raw_folder
    2. Merge all cleaned texts
    3. Write once to processed_folder/output_file
    """

    # Extract all PDFs
    extracted_dict = extract_from_folder(raw_folder)
    if not extracted_dict:
        print("No PDFs extracted. Exiting.")
        return

    # Merge all texts
    merged_text = ""
    for filename, text in extracted_dict.items():
        merged_text += f"\n--- {filename} ---\n{text}\n"

    # Ensure processed folder exists
    os.makedirs(processed_folder, exist_ok=True)

    output_path = os.path.join(processed_folder, output_file)

    # Write once
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(merged_text)

    print(f"Extraction complete! Cleaned text saved to {output_path}")


# Quick test when running directly
if __name__ == "__main__":
    RAW_FOLDER = "data/raw"
    PROCESSED_FOLDER = "data/processed"
    run_extraction(RAW_FOLDER, PROCESSED_FOLDER)
