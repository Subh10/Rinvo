"""Lazy TTS engine with a replaceable backend boundary."""
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any
import numpy as np

from rinvo.config import get_settings


class BackendUnavailableError(RuntimeError):
    """Raised when the configured model backend cannot be loaded."""


@dataclass
class SpeechResult:
    audio: np.ndarray
    sample_rate: int
    model_id: str


class TTSService:
    def __init__(
        self, backend: str, model_id: str, device: str = "auto", audio_prompt_path: str | None = None
    ) -> None:
        self.backend = backend.lower()
        self.model_id = model_id
        self.device = device
        self.audio_prompt_path = audio_prompt_path
        self._model: Any = None
        self._sample_rate: int | None = None

    def _load(self) -> None:
        if self._model is not None:
            return
        if self.backend == "mock":
            raise BackendUnavailableError(
                "The 'mock' backend does not synthesize speech. Install and configure a verified TTS backend."
            )
        if self.backend != "chatterbox_turbo":
            raise BackendUnavailableError(f"Unsupported backend '{self.backend}'.")
        if not self.audio_prompt_path:
            raise BackendUnavailableError(
                "Chatterbox-Turbo requires a reference voice recording. Set RINVO_AUDIO_PROMPT_PATH "
                "to a local, authorized audio file (for example, a clean ~10-second WAV clip)."
            )
        if not Path(self.audio_prompt_path).is_file():
            raise BackendUnavailableError(
                f"Reference audio file was not found: {self.audio_prompt_path}"
            )
        try:
            import torch
            from chatterbox.tts_turbo import ChatterboxTurboTTS
        except ImportError as exc:
            raise BackendUnavailableError(
                "Chatterbox-Turbo dependencies are unavailable. Follow the upstream installation instructions, "
                "then set RINVO_BACKEND=chatterbox_turbo."
            ) from exc
        device = self.device
        if device == "auto":
            device = "cuda" if torch.cuda.is_available() else "cpu"
        try:
            self._model = ChatterboxTurboTTS.from_pretrained(device=device)
            self._sample_rate = int(getattr(self._model, "sr", 24000))
        except Exception as exc:
            raise BackendUnavailableError(f"Could not initialize Chatterbox-Turbo: {exc}") from exc

    def synthesize(self, text: str) -> SpeechResult:
        self._load()
        try:
            generated = self._model.generate(text, audio_prompt_path=self.audio_prompt_path)
            if hasattr(generated, "detach"):
                generated = generated.detach().float().cpu().numpy()
            audio = np.asarray(generated, dtype=np.float32).squeeze()
            if audio.ndim != 1:
                raise ValueError("Expected the backend to return mono audio")
            if not audio.size:
                raise ValueError("Backend returned empty audio")
            return SpeechResult(audio=audio, sample_rate=self._sample_rate or 24000, model_id=self.model_id)
        except Exception as exc:
            raise BackendUnavailableError(f"Speech generation failed: {exc}") from exc


@lru_cache(maxsize=1)
def get_engine() -> TTSService:
    settings = get_settings()
    return TTSService(settings.backend, settings.model_id, settings.device, settings.audio_prompt_path)
