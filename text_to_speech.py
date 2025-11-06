from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan
import torch
import soundfile as sf
from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn
from datetime import datetime, timezone
from time import strftime
import os

app = FastAPI()

class Text(BaseModel):
    text: str

class SpeechOut(BaseModel):
    message: str
    file_path: str

PATH = "./audio_files"

processor = SpeechT5Processor.from_pretrained("microsoft/speecht5_tts")
model = SpeechT5ForTextToSpeech.from_pretrained("microsoft/speecht5_tts")
vocoder = SpeechT5HifiGan.from_pretrained("microsoft/speecht5_hifigan")

speaker_embeddings = torch.randn(1, 512) * 0.1


def clean_up(n=10):
    files = os.listdir(PATH)
    audio_files = []

    for file in files:
        if file.split('.')[1] == "wav":
            audio_files.append(file)

    audio_files.sort()

    for file_to_delete in audio_files[:-n]:
        os.remove(f"{PATH}/{file_to_delete}")


@app.post("/text_to_speech")
async def text_to_speech(text: Text):
    inputs = processor(text=text.text, return_tensors="pt")
    speech = model.generate_speech(inputs["input_ids"], speaker_embeddings, vocoder=vocoder)
    
    current_time = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")

    if not os.path.exists(PATH):
        os.makedirs(PATH)

    if len(os.listdir(PATH)) > 9:
        clean_up()

    output_path = f"./audio_files/output_speech_{current_time}.wav"
    sf.write(output_path, speech.numpy(), samplerate=16000)
    print(f"Audio saved to {output_path}")
    
    return FileResponse(output_path, media_type="audio/wav", filename="speech.wav")

@app.get("/")
async def home():
    return {"message": "running!"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7999)
