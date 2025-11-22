# tests/helpers_images.py
from PIL import Image, ImageFilter, ImageDraw
import io, numpy as np

def png_bytes(img: Image.Image) -> bytes:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

def black_image(w=256, h=256) -> bytes:
    return png_bytes(Image.new("RGB", (w, h), (0, 0, 0)))

def white_image(w=256, h=256) -> bytes:
    return png_bytes(Image.new("RGB", (w, h), (255, 255, 255)))

def noisy_image(w=256, h=256) -> bytes:
    arr = np.random.randint(0, 256, (h, w, 3), dtype=np.uint8)
    return png_bytes(Image.fromarray(arr, "RGB"))

def blurry_image(w=256, h=256) -> bytes:
    img = Image.new("RGB", (w, h), (120, 120, 120))
    draw = ImageDraw.Draw(img)
    draw.rectangle([40, 40, w - 40, h - 40], outline=(255, 255, 255), width=20)
    img = img.filter(ImageFilter.GaussianBlur(radius=8))
    return png_bytes(img)

def tiny_image() -> bytes:
    return png_bytes(Image.new("RGB", (32, 24), (200, 200, 200)))
