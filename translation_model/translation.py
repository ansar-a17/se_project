"""
Translation service using modern transformers library
FastAPI service for English to Dutch translation using MarianMT
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import MarianMTModel, MarianTokenizer
import torch
import uvicorn
from typing import Optional

app = FastAPI(title="Translation Service", version="1.0.0")

# Global variables for model and tokenizer
model = None
tokenizer = None

class TranslationRequest(BaseModel):
    text: str
    source_lang: str = "en"
    target_lang: str = "nl"

class TranslationResponse(BaseModel):
    original_text: str
    translated_text: str
    source_lang: str
    target_lang: str

@app.on_event("startup")
async def load_model():
    """Load the translation model on startup"""
    global model, tokenizer
    print("Loading Helsinki-NLP EN-NL translation model...")
    model_name = "Helsinki-NLP/opus-mt-en-nl"
    
    try:
        tokenizer = MarianTokenizer.from_pretrained(model_name)
        model = MarianMTModel.from_pretrained(model_name)
        print("Model loaded successfully!")
    except Exception as e:
        print(f"Error loading model: {e}")
        raise

def translate_text(text: str) -> str:
    """Translate English text to Dutch"""
    if model is None or tokenizer is None:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    try:
        inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
        
        with torch.no_grad():
            outputs = model.generate(**inputs, max_length=512)
        
        translation = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return translation
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation error: {str(e)}")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "Translation Service",
        "status": "running",
        "model": "Helsinki-NLP/opus-mt-en-nl",
        "source_language": "English",
        "target_language": "Dutch"
    }

@app.post("/translate", response_model=TranslationResponse)
async def translate(request: TranslationRequest):
    """
    Translate text from English to Dutch
    
    Args:
        request: TranslationRequest with text to translate
    
    Returns:
        TranslationResponse with original and translated text
    """
    if not request.text or not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    # Currently only supports EN -> NL
    if request.source_lang != "en" or request.target_lang != "nl":
        raise HTTPException(
            status_code=400, 
            detail="Only English to Dutch (en->nl) translation is currently supported"
        )
    
    try:
        translated = translate_text(request.text)
        
        return TranslationResponse(
            original_text=request.text,
            translated_text=translated,
            source_lang=request.source_lang,
            target_lang=request.target_lang
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model_loaded": model is not None and tokenizer is not None
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)
