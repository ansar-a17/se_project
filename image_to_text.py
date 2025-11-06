from PIL import Image
from transformers import pipeline
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
import io

app = FastAPI()

class TextOut(BaseModel):
    text: str

pipe = pipeline("image-to-text", model="Salesforce/blip-image-captioning-base")

@app.post("/image_to_text", response_model=TextOut)
async def image_to_text(file: UploadFile = File(...)):
    contents = await file.read()
    image = Image.open(io.BytesIO(contents))
    
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
    
    return TextOut(text=text)

@app.get("/")
async def home():
    return {"message": "running!"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)