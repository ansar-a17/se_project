from PIL import Image
from transformers import pipeline

def image_to_text(image: Image):
    pipe = pipeline("image-to-text", model="Salesforce/blip2-opt-2.7b")

    result = pipe(image)

    if isinstance(result, list):
        first = result[0]
        if isinstance(first, dict):
            text = first.get("generated_text", "")
        else:
            text = str(first)
    else:
        if isinstance(result, dict):
            text = result.get("generated_text", "")
        else:
            text = str(result)

    if text:
        text = text.strip()
        
    return text