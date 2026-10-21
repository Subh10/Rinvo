import pytest
from rinvo.engine import BackendUnavailableError, TTSService


def test_turbo_requires_reference_audio_before_importing_model():
    service = TTSService(
        backend="chatterbox_turbo",
        model_id="chatterbox-turbo",
        device="cpu",
        audio_prompt_path=None,
    )
    with pytest.raises(BackendUnavailableError, match="RINVO_AUDIO_PROMPT_PATH"):
        service.synthesize("Hello from Rinvo.")


def test_turbo_rejects_missing_reference_audio_file():
    service = TTSService(
        backend="chatterbox_turbo",
        model_id="chatterbox-turbo",
        device="cpu",
        audio_prompt_path="/this/file/should/not/exist/rinvo.wav",
    )
    with pytest.raises(BackendUnavailableError, match="was not found"):
        service.synthesize("Hello from Rinvo.")
