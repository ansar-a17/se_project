# tests/test_image_to_text.py
from fastapi.testclient import TestClient
from image_to_text.image_to_text import app
from tests.helpers_images import black_image, white_image, noisy_image, tiny_image

client = TestClient(app)

# Run "python -m pytest -q tests/test_image_to_text.py" for testing purposes.

def _post_image(img_bytes: bytes):
    files = {"file": ("test.png", img_bytes, "image/png")}
    return client.post("/image_to_text", files=files)

def test_black_image_returns_string():
    r = _post_image(black_image())
    assert r.status_code == 200
    data = r.json()
    assert "text" in data
    assert isinstance(data["text"], str)

def test_white_image_returns_string():
    r = _post_image(white_image())
    assert r.status_code == 200
    assert isinstance(r.json()["text"], str)

def test_noisy_image_returns_string():
    r = _post_image(noisy_image())
    assert r.status_code == 200
    assert isinstance(r.json()["text"], str)

def test_tiny_image_returns_string():
    r = _post_image(tiny_image())
    assert r.status_code == 200
    assert isinstance(r.json()["text"], str)
