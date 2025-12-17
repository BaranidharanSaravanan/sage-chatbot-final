import re
import string

def clean_text_basic(text: str) -> str:
    """
    Basic, universal cleanup safe for ALL PDFs.
    - Removes non-printable characters
    - Normalizes common PDF ligatures
    """
    if not text:
        return ""

    text = ''.join(c for c in text if c in string.printable)

    ligatures = {
        "ﬁ": "fi",
        "ﬂ": "fl",
        "ﬀ": "ff",
        "ﬃ": "ffi",
        "ﬄ": "ffl"
    }
    for k, v in ligatures.items():
        text = text.replace(k, v)

    return text


def clean_text(text: str) -> str:
    """
    Stronger cleanup for final output.
    - Collapses whitespace
    - Removes hyphenation at line breaks
    """
    if not text:
        return ""

    text = clean_text_basic(text)
    text = re.sub(r'(\w)-\s*\n\s*(\w)', r'\1\2', text)
    text = re.sub(r'\s+', ' ', text)


    return text.strip()


# 🔹 LOCAL TEST (REMOVE BEFORE COMMIT)
if __name__ == "__main__":
    sample = "This  is   a   test-\n text with ligatures ﬁ ﬂ  \n\n and spacing."
    print("Before:")
    print(sample)
    print("\nAfter:")
    print(clean_text(sample))
