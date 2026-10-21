"""Input validation helpers shared by API and SDK callers."""
from fastapi import HTTPException


def validate_text(text: str, max_chars: int) -> str:
    if not isinstance(text, str) or not text.strip():
        raise HTTPException(status_code=422, detail="'input' must contain non-whitespace text.")
    if len(text) > max_chars:
        raise HTTPException(
            status_code=413,
            detail=f"Input is too long ({len(text)} characters); maximum is {max_chars}.",
        )
    return text.strip()


def validate_format(response_format: str) -> str:
    if response_format.lower() != "wav":
        raise HTTPException(status_code=422, detail="Unsupported response_format. Supported: wav.")
    return "wav"
