import io
from unittest.mock import patch

import pytest

from action.client import synthesize


class FakeResponse:
    status = 200
    headers = {"Content-Type": "audio/wav"}

    def __init__(self, body):
        self.body = body

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return self.body


VALID_WAV_HEADER = b"RIFF" + (4).to_bytes(4, "little") + b"WAVE" + b"data"


def test_synthesize_saves_wav_and_returns_path(tmp_path):
    output = tmp_path / "nested" / "speech.wav"
    with patch("action.client.urlopen", return_value=FakeResponse(VALID_WAV_HEADER)) as mocked:
        result = synthesize("https://tts.example.com/", "Hello world", str(output))
    assert result == output
    assert output.read_bytes() == VALID_WAV_HEADER
    request = mocked.call_args.args[0]
    assert request.full_url == "https://tts.example.com/v1/audio/speech"
    assert request.get_method() == "POST"


def test_synthesize_sends_optional_bearer_token(tmp_path):
    with patch("action.client.urlopen", return_value=FakeResponse(VALID_WAV_HEADER)) as mocked:
        synthesize("https://tts.example.com", "Hello", str(tmp_path / "out.wav"), "secret")
    assert mocked.call_args.args[0].get_header("Authorization") == "Bearer secret"


@pytest.mark.parametrize("api_url,text", [("", "hello"), ("https://tts.example.com", "  ")])
def test_synthesize_rejects_missing_inputs(api_url, text, tmp_path):
    with pytest.raises(ValueError):
        synthesize(api_url, text, str(tmp_path / "out.wav"))


def test_synthesize_rejects_non_wav_response(tmp_path):
    with patch("action.client.urlopen", return_value=FakeResponse(b"<html>oops</html>")):
        with pytest.raises(RuntimeError, match="not a valid RIFF/WAVE"):
            synthesize("https://tts.example.com", "Hello", str(tmp_path / "out.wav"))
