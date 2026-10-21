# Installation

1. Use Python 3.11 in a fresh virtual environment.
2. Install Rinvo with `pip install -e '.[dev,demo]'`.
3. Run `pytest` to verify the API and utility layer.
4. Start the API with `uvicorn rinvo.api:app --host 127.0.0.1 --port 8000`.
5. The default `mock` backend intentionally does not generate speech. Follow the current upstream Chatterbox-Turbo installation instructions, confirm license compatibility, then set `RINVO_BACKEND=chatterbox_turbo` and test on supported hardware.

The upstream model's install steps may change. Do not assume the model is installed merely because Rinvo's package installs.
