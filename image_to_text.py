from PIL import Image
from transformers import pipeline

pipe = pipeline("image-text-to-text", model="Salesforce/blip2-opt-2.7b")

img = Image.open("example.png")
result = pipe(img)

if isinstance(result, list):
    text = result[0].get("generated_text", result[0])
else:
    text = result

print(text)