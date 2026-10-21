"""FastAPI application exposing Rinvo's speech-generation API."""
from typing import Literal
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field

from rinvo import __version__
from rinvo.audio import to_wav_bytes
from rinvo.config import get_settings
from rinvo.engine import BackendUnavailableError, get_engine
from rinvo.validation import validate_format, validate_text

app = FastAPI(title="Rinvo API", version=__version__, description="Self-hostable text-to-speech API")


class SpeechRequest(BaseModel):
    input: str = Field(..., description="Text to synthesize")
    response_format: Literal["wav"] = "wav"


@app.get("/health")
def health() -> dict[str, str | bool]:
    settings = get_settings()
    return {"status": "ok", "backend": settings.backend, "model_id": settings.model_id}


@app.get("/v1/models")
def models() -> dict[str, list[dict[str, str]]]:
    settings = get_settings()
    return {"data": [{"id": settings.model_id, "object": "model", "backend": settings.backend}]}


@app.post("/v1/audio/speech", response_class=Response, responses={200: {"content": {"audio/wav": {}}}})
def create_speech(request: SpeechRequest) -> Response:
    settings = get_settings()
    text = validate_text(request.input, settings.max_text_chars)
    validate_format(request.response_format)
    try:
        result = get_engine().synthesize(text)
        payload = to_wav_bytes(result.audio, result.sample_rate)
    except BackendUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=500, detail=f"Could not encode audio: {exc}") from exc
    return Response(
        content=payload,
        media_type="audio/wav",
        headers={"X-Rinvo-Model": result.model_id, "Content-Disposition": 'attachment; filename="rinvo.wav"'},
    )
