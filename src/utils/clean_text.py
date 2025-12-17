# utils/clean_text.py

import re
import string

def clean_text(text: str) -> str:
    """
    Clean the input text and return a standardized version.
    Steps:
    1. Remove non-printable/control characters
    2. Replace multiple spaces, tabs, newlines with a single space
    3. Strip leading/trailing whitespace
    4. Optional: normalize common PDF ligatures or hyphens
    """
    if not text:
        return ""

    # Remove non-printable characters
    text = ''.join(c for c in text if c in string.printable)

    # Replace ligatures often seen in PDFs
    ligatures = {
        "ﬁ": "fi",
        "ﬂ": "fl",
        "ﬀ": "ff",
        "ﬃ": "ffi",
        "ﬄ": "ffl"
    }
    for k, v in ligatures.items():
        text = text.replace(k, v)

    # Replace multiple spaces/tabs/newlines with a single space
    text = re.sub(r'\s+', ' ', text)

    # Remove hyphenation at line breaks (e.g., "exam-\nple" → "example")
    text = re.sub(r'-\s+', '', text)

    # Strip leading/trailing whitespace
    text = text.strip()

    return text


# Quick test when running directly
if __name__ == "__main__":
    sample_text = "This is   a  sample \n\n PDF\ttext with  weird  spacing and ligatures ﬁ, ﬂ, ﬀ."
    print("Before cleaning:")
    print(sample_text)
    print("\nAfter cleaning:")
    print(clean_text(sample_text))
