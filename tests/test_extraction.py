# tests/test_extraction.py

import os
import pytest
from src.data_extraction.extract_base import extract_from_pdf_fitz

DATA_DIR = "data/raw"


def test_extract_valid_pdf():
    """Test extraction works on a valid PDF"""
    pdf_path = os.path.join(DATA_DIR, "student_life.pdf")
    if not os.path.exists(pdf_path):
        pytest.skip("PDF not available for test")

    text = extract_from_pdf_fitz(pdf_path)
    assert isinstance(text, str)
    assert len(text) > 0


def test_extract_non_existent_pdf():
    """Test extractor raises error for missing file"""
    with pytest.raises(Exception):
        extract_from_pdf_fitz("data/raw/does_not_exist.pdf")


def test_extract_empty_pdf(tmp_path):
    """Test extractor handles empty PDF safely"""
    empty_pdf = tmp_path / "empty.pdf"
    empty_pdf.write_bytes(b"")

    with pytest.raises(Exception):
        extract_from_pdf_fitz(str(empty_pdf))
