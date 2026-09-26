from app.handlers import split_message


def test_split_message_keeps_short_text() -> None:
    assert split_message("Коротка відповідь") == ["Коротка відповідь"]


def test_split_message_respects_limit() -> None:
    chunks = split_message("слово " * 30, limit=40)

    assert len(chunks) > 1
    assert all(len(chunk) <= 40 for chunk in chunks)
    assert " ".join(chunks).split() == ("слово " * 30).split()

