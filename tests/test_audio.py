import io
import numpy as np
import soundfile as sf
import pytest
from rinvo.audio import to_wav_bytes


def test_audio_is_valid_wav():
    payload = to_wav_bytes(np.zeros(2400, dtype=np.float32), 24000)
    audio, rate = sf.read(io.BytesIO(payload))
    assert rate == 24000
    assert len(audio) == 2400


def test_audio_rejects_empty_output():
    with pytest.raises(ValueError, match="empty"):
        to_wav_bytes(np.array([], dtype=np.float32), 24000)
