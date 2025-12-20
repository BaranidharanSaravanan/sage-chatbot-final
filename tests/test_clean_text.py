from src.utils.clean_text import clean_text, clean_text_basic


def test_clean_text_basic_removes_non_printable():
    text = "Hello\x0cWorld"
    cleaned = clean_text_basic(text)
    assert "World" in cleaned


def test_clean_text_basic_ligatures():
    text = "ﬁ ﬂ ﬀ ﬃ ﬄ"
    cleaned = clean_text_basic(text)
    # Ligatures are removed, not expanded
    assert cleaned.strip() == ""




def test_clean_text_collapses_whitespace():
    text = "This   is    a   test"
    cleaned = clean_text(text)
    assert cleaned == "This is a test"


def test_clean_text_removes_hyphenation():
    text = "exam-\nple"
    cleaned = clean_text(text)
    assert cleaned == "example"
