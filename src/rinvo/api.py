"""FastAPI application exposing Rinvo's speech-generation API."""
from contextlib import asynccontextmanager
import logging
from time import perf_counter
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field

from rinvo import __version__
from rinvo.audio import to_wav_bytes
from rinvo.config import get_settings
from rinvo.engine import BackendUnavailableError, get_engine
from rinvo.validation import validate_format, validate_text

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings = get_settings()
    if settings.backend != "mock" and settings.warmup_on_startup:
        try:
            get_engine().warmup()
            logger.info("Rinvo model warm-up completed")
        except BackendUnavailableError:
            # Keep the process observable; readiness reports false and synthesis returns 503.
            logger.exception("Rinvo model warm-up failed")
    yield


app = FastAPI(
    title="Rinvo API",
    version=__version__,
    description="Self-hostable text-to-speech API",
    lifespan=lifespan,
)


class SpeechRequest(BaseModel):
    input: str = Field(..., description="Text to synthesize")
    response_format: Literal["wav"] = "wav"


@app.get("/health")
def health() -> dict[str, str | bool]:
    settings = get_settings()
    return {
        "status": "ok",
        "backend": settings.backend,
        "model_id": settings.model_id,
        "model_ready": get_engine().is_ready,
    }


@app.get("/ready")
def readiness() -> dict[str, str | bool]:
    settings = get_settings()
    ready = get_engine().is_ready
    if not ready:
        raise HTTPException(
            status_code=503,
            detail="TTS model is not ready. Check backend configuration and model initialization.",
        )
    return {"status": "ready", "backend": settings.backend, "model_id": settings.model_id}


@app.get("/v1/models")
def models() -> dict[str, list[dict[str, str]]]:
    settings = get_settings()
    return {"data": [{"id": settings.model_id, "object": "model", "backend": settings.backend}]}


@app.post("/v1/audio/speech", response_class=Response, responses={200: {"content": {"audio/wav": {}}}})
def create_speech(request: SpeechRequest) -> Response:
    settings = get_settings()
    text = validate_text(request.input, settings.max_text_chars)
    validate_format(request.response_format)
    started = perf_counter()
    try:
        result = get_engine().synthesize(text)
        generated_at = perf_counter()
        payload = to_wav_bytes(result.audio, result.sample_rate)
        finished = perf_counter()
    except BackendUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=500, detail=f"Could not encode audio: {exc}") from exc

    audio_seconds = len(result.audio) / result.sample_rate
    generation_ms = (generated_at - started) * 1000
    return Response(
        content=payload,
        media_type="audio/wav",
        headers={
            "X-Rinvo-Model": result.model_id,
            "X-Rinvo-Generation-Ms": f"{generation_ms:.2f}",
            "X-Rinvo-Audio-Duration-S": f"{audio_seconds:.3f}",
            "X-Rinvo-Real-Time-Factor": f"{generation_ms / 1000 / audio_seconds:.4f}" if audio_seconds else "unknown",
            "X-Rinvo-Encoding-Ms": f"{(finished - generated_at) * 1000:.2f}",
            "Content-Disposition": 'attachment; filename="rinvo.wav"',
        },
    )
