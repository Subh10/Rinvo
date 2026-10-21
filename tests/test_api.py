from fastapi.testclient import TestClient
from rinvo.api import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_models():
    response = client.get("/v1/models")
    assert response.status_code == 200
    assert response.json()["data"][0]["object"] == "model"


def test_blank_text_rejected():
    response = client.post("/v1/audio/speech", json={"input": "   ", "response_format": "wav"})
    assert response.status_code == 422


def test_unsupported_format_rejected():
    response = client.post("/v1/audio/speech", json={"input": "hello", "response_format": "mp3"})
    assert response.status_code == 422


def test_mock_backend_does_not_claim_to_generate_audio():
    response = client.post("/v1/audio/speech", json={"input": "hello", "response_format": "wav"})
    assert response.status_code == 503
    assert "does not synthesize speech" in response.json()["detail"]
