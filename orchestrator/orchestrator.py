from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import uvicorn
import logging
from datetime import datetime, timezone
import os
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Screenshot Orchestrator Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

IMAGE_TO_TEXT_URL = os.getenv("IMAGE_TO_TEXT_URL", "http://localhost:8000")
TEXT_TO_SPEECH_URL = os.getenv("TEXT_TO_SPEECH_URL", "http://localhost:7999")
TRANSLATION_URL = os.getenv("TRANSLATION_URL", "http://localhost:8003")

TIMEOUT = 120.0


@app.get("/")
async def home():
    return {
        "service": "Screenshot Orchestrator",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "process": "/process_screenshot (POST)"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    health_status = {
        "orchestrator": "healthy",
        "image_to_text": "unknown",
        "text_to_speech": "unknown",
        "translation": "unknown",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    # Check image_to_text service
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{IMAGE_TO_TEXT_URL}/")
            if response.status_code == 200:
                health_status["image_to_text"] = "healthy"
    except Exception as e:
        health_status["image_to_text"] = f"unhealthy: {str(e)}"
        logger.warning(f"Image-to-text service health check failed: {e}")
    
    # Check text_to_speech service
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{TEXT_TO_SPEECH_URL}/")
            if response.status_code == 200:
                health_status["text_to_speech"] = "healthy"
    except Exception as e:
        health_status["text_to_speech"] = f"unhealthy: {str(e)}"
        logger.warning(f"Text-to-speech service health check failed: {e}")
    
    # Check translation service
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{TRANSLATION_URL}/health")
            if response.status_code == 200:
                health_status["translation"] = "healthy"
    except Exception as e:
        health_status["translation"] = f"unhealthy: {str(e)}"
        logger.warning(f"Translation service health check failed: {e}")
    
    return health_status


@app.post("/process_screenshot")
async def process_screenshot(
    file: UploadFile = File(...),
    translate: bool = Query(False, description="Translate text to Dutch before speech synthesis")
):
    """
    Main orchestration endpoint:
    1. Receives screenshot from frontend
    2. Sends to image_to_text service
    3. (Optional) Translates text to Dutch if translate=true
    4. Sends result to text_to_speech service
    5. Returns audio file to frontend
    """
    logger.info(f"Processing screenshot: {file.filename}, translate={translate}")
    
    try:
        # Read the uploaded file
        image_content = await file.read()
        logger.info(f"Received image file, size: {len(image_content)} bytes")
        
        # Step 1: Send image to image_to_text service
        logger.info("Step 1: Sending image to image_to_text service...")
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            files = {"file": (file.filename, image_content, file.content_type)}
            response = await client.post(
                f"{IMAGE_TO_TEXT_URL}/image_to_text",
                files=files
            )
            response.raise_for_status()
            image_result = response.json()
        
        text = image_result.get("text", "").strip()
        if not text:
            raise HTTPException(
                status_code=422,
                detail="Image analysis returned empty text. Please try another screenshot."
            )
        
        logger.info(f"Image analysis complete. Text: {text[:100]}...")
        return await process_text_to_speech(text, translate)
        
    except httpx.TimeoutException as e:
        logger.error(f"Timeout error: {e}")
        raise HTTPException(
            status_code=504,
            detail="Request timed out. The AI models may be loading or the request is too large."
        )
    
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error from downstream service: {e}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Downstream service error: {e.response.text}"
        )
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


class TextRequest(BaseModel):
    text: str


@app.post("/process_text")
async def process_text(
    request: TextRequest,
    translate: bool = Query(False, description="Translate text to Dutch before speech synthesis")
):
    """
    Text-only orchestration endpoint:
    1. Receives text from frontend
    2. (Optional) Translates text to Dutch if translate=true
    3. Sends result to text_to_speech service
    4. Returns audio file to frontend
    """
    logger.info(f"Processing text input, translate={translate}")
    
    try:
        text = request.text.strip()
        if not text:
            raise HTTPException(
                status_code=422,
                detail="Text cannot be empty."
            )
        
        logger.info(f"Received text: {text[:100]}...")
        return await process_text_to_speech(text, translate)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


async def process_text_to_speech(text: str, translate: bool = False):
    """
    Helper function to process text through translation and TTS
    """
    try:
        original_text = text
        
        # Step: (Optional) Translate text to Dutch
        if translate:
            logger.info("Translating text to Dutch...")
            try:
                async with httpx.AsyncClient(timeout=TIMEOUT) as client:
                    response = await client.post(
                        f"{TRANSLATION_URL}/translate",
                        json={"text": text, "source_lang": "en", "target_lang": "nl"}
                    )
                    response.raise_for_status()
                    translation_result = response.json()
                
                text = translation_result.get("translated_text", text)
                logger.info(f"Translation complete. Translated text: {text[:100]}...")
            except Exception as e:
                logger.warning(f"Translation failed, using original text: {e}")
                # Continue with original text if translation fails
        
        # Step: Send text to text_to_speech service
        logger.info("Sending text to text_to_speech service...")
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.post(
                f"{TEXT_TO_SPEECH_URL}/text_to_speech",
                json={"text": text}
            )
            response.raise_for_status()
            audio_content = response.content
        
        logger.info(f"Text-to-speech complete. Audio size: {len(audio_content)} bytes")
        
        # Save audio temporarily
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")
        temp_audio_path = f"/tmp/orchestrator_audio_{timestamp}.wav"
        
        with open(temp_audio_path, "wb") as f:
            f.write(audio_content)
        
        # Return the audio file with the text in headers
        headers = {
            "X-Caption-Text": text,
            "X-Processing-Complete": "true"
        }
        
        if translate:
            headers["X-Original-Text"] = original_text
            headers["X-Translated"] = "true"
        
        return FileResponse(
            temp_audio_path,
            media_type="audio/wav",
            filename="speech.wav",
            headers=headers
        )
        
    except httpx.TimeoutException as e:
        logger.error(f"Timeout error: {e}")
        raise HTTPException(
            status_code=504,
            detail="Request timed out. The AI models may be loading or the request is too large."
        )
    
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error from downstream service: {e}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Downstream service error: {e.response.text}"
        )
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
