"""Minimal Python example calling the Rinvo HTTP API."""
import argparse
import json
import urllib.request

parser = argparse.ArgumentParser()
parser.add_argument("text", nargs="?", default="Welcome to Rinvo.")
parser.add_argument("--url", default="http://127.0.0.1:8000")
parser.add_argument("--output", default="rinvo.wav")
args = parser.parse_args()
request = urllib.request.Request(
    f"{args.url.rstrip('/')}/v1/audio/speech",
    data=json.dumps({"input": args.text, "response_format": "wav"}).encode(),
    headers={"Content-Type": "application/json"},
    method="POST",
)
with urllib.request.urlopen(request, timeout=300) as response:
    with open(args.output, "wb") as audio_file:
        audio_file.write(response.read())
print(f"Saved {args.output}")
