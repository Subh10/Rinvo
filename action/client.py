"""GitHub Actions client for a running Rinvo speech API."""
from __future__ import annotations

import json
import os
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def synthesize(
    api_url: str,
    text: str,
    output_path: str,
    bearer_token: str = "",
    timeout_seconds: int = 180,
) -> Path:
    """Call Rinvo's speech endpoint and save a validated WAV response."""
    if not api_url.strip():
        raise ValueError("api_url is required")
    if not text.strip():
        raise ValueError("text must not be empty")
    if timeout_seconds < 1:
        raise ValueError("timeout_seconds must be positive")

    endpoint = api_url.rstrip("/") + "/v1/audio/speech"
    headers = {"Content-Type": "application/json", "Accept": "audio/wav"}
    if bearer_token.strip():
        headers["Authorization"] = f"Bearer {bearer_token.strip()}"
    request = Request(
        endpoint,
        data=json.dumps({"input": text, "response_format": "wav"}).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            audio = response.read()
            content_type = response.headers.get("Content-Type", "").split(";")[0].lower()
            if response.status < 200 or response.status >= 300:
                raise RuntimeError(f"Rinvo API returned HTTP {response.status}")
            if content_type not in {"audio/wav", "audio/x-wav", "application/octet-stream"}:
                raise RuntimeError(f"Expected WAV audio, received Content-Type: {content_type or 'missing'}")
    except HTTPError as exc:
        # Avoid printing response bodies that might contain deployment-specific details.
        raise RuntimeError(f"Rinvo API returned HTTP {exc.code}") from exc
    except URLError as exc:
        raise RuntimeError(f"Could not reach the Rinvo API: {exc.reason}") from exc

    if len(audio) < 12 or audio[:4] != b"RIFF" or audio[8:12] != b"WAVE":
        raise RuntimeError("Rinvo API response was not a valid RIFF/WAVE file")

    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(audio)

    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a", encoding="utf-8") as output:
            output.write(f"audio_path={destination.as_posix()}\n")
    print(f"Rinvo generated a WAV file at {destination}")
    return destination


def main() -> None:
    synthesize(
        api_url=os.environ.get("INPUT_API_URL", ""),
        text=os.environ.get("INPUT_TEXT", ""),
        output_path=os.environ.get("INPUT_OUTPUT_PATH", "rinvo-output.wav"),
        bearer_token=os.environ.get("INPUT_BEARER_TOKEN", ""),
        timeout_seconds=int(os.environ.get("INPUT_TIMEOUT_SECONDS", "180")),
    )


if __name__ == "__main__":
    main()
