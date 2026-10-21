"""Audio encoding helpers."""
from io import BytesIO
import numpy as np
import soundfile as sf


def to_wav_bytes(audio: np.ndarray, sample_rate: int) -> bytes:
    if sample_rate <= 0:
        raise ValueError("sample_rate must be positive")
    samples = np.asarray(audio, dtype=np.float32)
    if samples.size == 0:
        raise ValueError("audio output is empty")
    if samples.ndim not in (1, 2):
        raise ValueError("audio must be a mono or multi-channel array")
    if not np.isfinite(samples).all():
        raise ValueError("audio contains non-finite samples")
    buffer = BytesIO()
    sf.write(buffer, samples, sample_rate, format="WAV", subtype="PCM_16")
    return buffer.getvalue()
