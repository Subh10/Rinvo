# Installation

1. Use Python 3.11 in a fresh virtual environment.
2. Install Rinvo with `pip install -e '.[dev,demo]'`.
3. Run `pytest` to verify the API and utility layer.
4. Start the API with `uvicorn rinvo.api:app --host 127.0.0.1 --port 8000`.
5. The default `mock` backend intentionally does not generate speech. Follow the current upstream Chatterbox installation instructions, confirm license compatibility, then set `RINVO_BACKEND=chatterbox_turbo` and test on supported hardware.
6. Chatterbox-Turbo's documented generation API requires `audio_prompt_path`. Set `RINVO_AUDIO_PROMPT_PATH` to a local, authorized reference recording. Never commit private voice recordings to the repository.

The upstream model's install steps may change. The upstream README currently documents `pip install chatterbox-tts` and imports `ChatterboxTurboTTS` from `chatterbox.tts_turbo`; verify these instructions against the current upstream documentation before installing.
