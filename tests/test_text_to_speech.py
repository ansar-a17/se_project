# tests/test_text_to_speech.py
from fastapi.testclient import TestClient
from text_to_speech.text_to_speech import app

#Run "python -m pytest -q tests/test_text_to_speech.py" for testing purposes.

client = TestClient(app)

def test_tts_happy_path_returns_audio():
    r = client.post("/text_to_speech", json={"text": "hello world"})
    assert r.status_code == 200
    # content-type should be audio (often audio/wav)
    assert r.headers.get("content-type", "").startswith("audio/")
    # should not be empty
    assert len(r.content) > 100

def test_tts_rejects_empty_text():
    r = client.post("/text_to_speech", json={"text": ""})
    assert r.status_code in (400, 422)
