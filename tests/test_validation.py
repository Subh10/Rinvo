import pytest
from fastapi import HTTPException
from rinvo.validation import validate_format, validate_text


def test_validate_text_strips_outer_whitespace():
    assert validate_text("  hello  ", 10) == "hello"


@pytest.mark.parametrize("value", ["", "   ", "\n\t"])
def test_validate_text_rejects_blank(value):
    with pytest.raises(HTTPException) as exc:
        validate_text(value, 10)
    assert exc.value.status_code == 422


def test_validate_text_rejects_too_long():
    with pytest.raises(HTTPException) as exc:
        validate_text("12345", 4)
    assert exc.value.status_code == 413


def test_only_wav_is_supported():
    assert validate_format("wav") == "wav"
    with pytest.raises(HTTPException) as exc:
        validate_format("mp3")
    assert exc.value.status_code == 422
