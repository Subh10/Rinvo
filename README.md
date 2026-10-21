# Rinvo

**Give your words a voice.**

Rinvo is an open-source, self-hostable text-to-speech (TTS) service with a Python interface, REST API, and browser demo. It separates the product/API layer from the underlying speech model so the backend can be replaced without changing the public API.

> **Status:** MVP scaffold. The API and validation layer are implemented; the Chatterbox-Turbo backend must be installed and tested on a compatible machine before claiming end-to-end speech generation works. Model code, weights, and licenses are separate from Rinvo's code.

## Features

- FastAPI endpoint: `POST /v1/audio/speech`
- Health and model discovery endpoints
- Input validation and configurable text length
- Optional Gradio demo
- WAV responses
- Lazy model loading and explicit errors when the backend is unavailable
- Pytest suite and GitHub Actions CI

## Quick start

Python 3.11 is recommended. Create a virtual environment and install the API dependencies:

```bash
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
pip install -e '.[dev,demo]'
cp .env.example .env  # Windows: copy .env.example .env
```

Start the API:

```bash
uvicorn rinvo.api:app --host 127.0.0.1 --port 8000
```

Open the interactive API docs at http://127.0.0.1:8000/docs and check http://127.0.0.1:8000/health.

### Generate speech

```bash
curl -X POST http://127.0.0.1:8000/v1/audio/speech \\
  -H 'Content-Type: application/json' \\
  -d '{"input":"Welcome to Rinvo.","response_format":"wav"}' \\
  --output rinvo.wav
```

The speech endpoint requires the optional model backend and its compatible dependencies. Install and verify these using the upstream Chatterbox-Turbo project instructions and license terms before enabling it. Rinvo does not bundle model weights.

### Run the browser demo

```bash
python demo/app.py
```

Set `RINVO_BACKEND=chatterbox_turbo` after the backend has been installed and verified. The demo uses the same inference engine as the API.

## Configuration

See `.env.example`. The backend defaults to `mock`, which is useful for tests and API integration checks but does **not** synthesize speech. Set `RINVO_BACKEND=chatterbox_turbo` to request real inference; the process will return a clear error if the backend is not installed or initialized.

## API

### `POST /v1/audio/speech`

Request:

```json
{
  "input": "Welcome to Rinvo.",
  "response_format": "wav"
}
```

Successful requests return `audio/wav`. Empty text, excessive input, and unsupported formats return a 4xx response. Model/backend errors return a clear server error rather than fabricated audio.

### `GET /health`

Returns service health and the configured backend name. This is a process-level health check; it does not guarantee that model weights are available.

### `GET /v1/models`

Returns the configured model/backend identifier.

## Development

```bash
pip install -e '.[dev]'
pytest
```

The tests cover validation, health/model endpoints, and error handling without downloading model weights. A real-model smoke test and benchmark should be run separately on supported hardware.

## Licensing and provenance

- Original Rinvo source code is licensed under MIT; see [LICENSE](LICENSE).
- The selected TTS backend, pretrained checkpoint, dependencies, and assets may have separate terms. Review the exact upstream license and model card before commercial use or redistribution.
- Rinvo does not claim to have trained the upstream model.
- Do not synthesize or clone a person's voice without appropriate authorization. Do not commit private recordings, credentials, or model weights.

See [docs/licensing.md](docs/licensing.md), [docs/security.md](docs/security.md), and [docs/model-card.md](docs/model-card.md).

## Roadmap

- [x] API contract, validation, backend abstraction, tests, docs scaffold
- [ ] Verify upstream model installation and licensing
- [ ] End-to-end real audio generation on documented hardware
- [ ] Docker validation and reproducible baseline benchmark
- [ ] External clean-install verification

## Contributing

Issues and pull requests are welcome. See [CONTRIBUTING.md](.github/CONTRIBUTING.md).
