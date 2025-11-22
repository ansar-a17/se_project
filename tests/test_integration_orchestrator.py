# tests/test_integration_orchestrator.py
import httpx
import respx
from fastapi.testclient import TestClient
import orchestrator.orchestrator as orch   # import the module so we can patch attributes
from orchestrator.orchestrator import app

# When testing, run "python -m pytest -q tests/test_integration_orchestrator.py".
# After testing, an audio wave file may appear in the project. You can safely delete the file.

client = TestClient(app)

@respx.mock
def test_orch_happy_path_returns_audio(monkeypatch):
    # Patch the module-level URLs that the orchestrator actually uses
    monkeypatch.setattr(orch, "IMAGE_TO_TEXT_URL", "http://imag")
    monkeypatch.setattr(orch, "TEXT_TO_SPEECH_URL", "http://tts")

    # Mock downstreams
    respx.post("http://imag/image_to_text").mock(
        return_value=httpx.Response(200, json={"text": "a cat"})
    )
    fake_wav = b"RIFF....WAVEfmt " + b"\x00" * 200
    respx.post("http://tts/text_to_speech").mock(
        return_value=httpx.Response(200, content=fake_wav, headers={"content-type": "audio/wav"})
    )

    files = {"file": ("x.png", b"\x89PNG...", "image/png")}
    r = client.post("/process_screenshot", files=files)

    assert r.status_code == 200
    assert r.headers.get("content-type", "").startswith("audio/")
    assert r.headers.get("X-Caption-Text") == "a cat"
    assert len(r.content) > 100


@respx.mock
def test_orch_handles_empty_caption(monkeypatch):
    monkeypatch.setattr(orch, "IMAGE_TO_TEXT_URL", "http://imag")
    monkeypatch.setattr(orch, "TEXT_TO_SPEECH_URL", "http://tts")

    respx.post("http://imag/image_to_text").mock(
        return_value=httpx.Response(200, json={"text": ""})
    )
    # Even if TTS were called, return 500; orchestrator should reject earlier
    respx.post("http://tts/text_to_speech").mock(return_value=httpx.Response(500))

    files = {"file": ("x.png", b"png", "image/png")}
    r = client.post("/process_screenshot", files=files)

    assert r.status_code == 422
    assert "empty text" in r.text.lower()


@respx.mock
def test_orch_timeout_from_tts(monkeypatch):
    monkeypatch.setattr(orch, "IMAGE_TO_TEXT_URL", "http://imag")
    monkeypatch.setattr(orch, "TEXT_TO_SPEECH_URL", "http://tts")

    respx.post("http://imag/image_to_text").mock(
        return_value=httpx.Response(200, json={"text": "hello"})
    )

    def raise_timeout(request):
        raise httpx.TimeoutException("boom")

    respx.post("http://tts/text_to_speech").mock(side_effect=raise_timeout)

    files = {"file": ("x.png", b"png", "image/png")}
    r = client.post("/process_screenshot", files=files)

    assert r.status_code == 504
    assert "timed out" in r.text.lower()

