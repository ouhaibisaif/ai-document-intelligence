from app.utils.text import clean_text, split_text


def test_clean_text_removes_nulls_and_extra_whitespace():
    assert clean_text("  a\x00b \t\t c\n\n\n\nd  ") == "a b c\n\nd"


def test_split_text_empty():
    assert split_text("") == []


def test_split_text_short_text_is_one_chunk():
    assert split_text("hello world") == ["hello world"]


def test_split_text_respects_size_and_overlap():
    text = "".join(str(i % 10) for i in range(3000))
    chunks = split_text(text, chunk_size=1200, overlap=160)
    assert all(len(c) <= 1200 for c in chunks)
    assert chunks[0][-160:] == chunks[1][:160]  # consecutive chunks overlap
    assert "".join(c[160:] if i else c for i, c in enumerate(chunks)) == text  # nothing lost
