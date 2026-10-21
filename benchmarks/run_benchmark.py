"""Basic latency benchmark for an already-running Rinvo API; not a quality score."""
import json
import statistics
import time
import urllib.request
from pathlib import Path

BASE_URL = "http://127.0.0.1:8000"
CASES = json.loads((Path(__file__).parent / "test_sentences.json").read_text())
results = []
for case in CASES:
    request = urllib.request.Request(
        f"{BASE_URL}/v1/audio/speech",
        data=json.dumps({"input": case["text"], "response_format": "wav"}).encode(),
        headers={"Content-Type": "application/json"}, method="POST",
    )
    start = time.perf_counter()
    with urllib.request.urlopen(request, timeout=300) as response:
        audio = response.read()
        content_type = response.headers.get("Content-Type", "")
    elapsed = time.perf_counter() - start
    results.append({"id": case["id"], "seconds": round(elapsed, 4), "bytes": len(audio), "content_type": content_type})
print(json.dumps({"base_url": BASE_URL, "cases": results, "median_seconds": statistics.median(r["seconds"] for r in results)}, indent=2))
print("Record GPU/model versions and repeat the run before comparing systems.")
