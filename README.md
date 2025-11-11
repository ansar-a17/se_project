# Screenshot to Audio Pipeline

A containerized microservices application that converts screenshots into audio narration using AI models.

## 🎯 Overview

This project orchestrates a pipeline that:
1. **Image to Text**: Analyzes screenshots and extracts text descriptions using the Salesforce BLIP image captioning model
2. **Text to Speech**: Converts extracted text into natural-sounding audio using Microsoft's SpeechT5 model
3. **Frontend**: Provides a user-friendly web interface for uploading screenshots and downloading audio

## 🏗️ Architecture

The application uses a microservices architecture with Docker containerization:

- **Frontend Service** (Port 3000): Web UI built with TypeScript, Vite, and Nginx
- **Orchestrator Service** (Port 5000): FastAPI backend that coordinates the pipeline
- **Image-to-Text Service** (Port 8000): FastAPI service for image captioning
- **Text-to-Speech Service** (Port 7999): FastAPI service for audio generation
- **Audio Storage**: Volume-mounted directory for generated audio files

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Windows PowerShell or compatible terminal

### Running the Application

```powershell
docker compose up -d --build
```

The application will be available at:
- **Frontend**: http://localhost:3000
- **Orchestrator API**: http://localhost:5000
- **Health Check**: http://localhost:5000/health

### Stopping the Application

```powershell
docker compose down
```

## 📁 Project Structure

```
.
├── docker-compose.yml          # Service orchestration configuration
├── requirements.txt             # Root Python dependencies
├── audio_files/                 # Volume for generated audio output
├── frontend/                    # Web UI service
│   ├── Dockerfile
│   ├── index.html
│   ├── nginx.conf
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── src/
├── orchestrator/               # Pipeline orchestration service
│   ├── Dockerfile
│   └── orchestrator.py
├── image_to_text/             # Image captioning service
│   ├── Dockerfile
│   ├── image_to_text.py
│   └── requirements.txt
└── text_to_speech/            # Audio synthesis service
    ├── Dockerfile
    ├── text_to_speech.py
    └── requirements.txt
```

## 🔄 Pipeline Flow

1. User uploads a screenshot via the frontend
2. Orchestrator receives the image and forwards it to the image-to-text service
3. Image-to-text service generates a text description
4. Orchestrator sends the text to the text-to-speech service
5. Text-to-speech service synthesizes audio and saves it
6. Audio file is returned to the frontend and made available for download

## 🛠️ API Endpoints

### Orchestrator Service
- `GET /` - Service information
- `GET /health` - Health status of all services
- `POST /process_screenshot` - Main endpoint to process a screenshot

### Image-to-Text Service
- `GET /` - Service status
- `POST /image_to_text` - Convert image to text

### Text-to-Speech Service
- `GET /` - Service status
- `POST /text_to_speech` - Convert text to speech

## 🧠 AI Models Used

- **Image Captioning**: Salesforce BLIP (`Salesforce/blip-image-captioning-base`)
- **Text-to-Speech**: Microsoft SpeechT5 (`microsoft/speecht5_tts`) with HiFi-GAN vocoder

## 📊 Health Checks

All services include health checks configured in the Docker Compose file:
- Services check connectivity every 30 seconds
- Orchestrator depends on both AI services being healthy before accepting requests
- Frontend depends on the orchestrator service

## 📦 Dependencies

Key Python packages:
- **FastAPI** - Web framework for API services
- **Transformers** - Hugging Face library for AI models
- **PyTorch** - Deep learning framework
- **Pillow** - Image processing
- **SoundFile** - Audio file I/O
- **Axios** - Frontend HTTP client

## 🔐 CORS Configuration

The orchestrator service allows requests from any origin (`allow_origins=["*"]`), making it suitable for development environments.

## 📝 Notes

- Generated audio files are automatically managed (up to 10 most recent files retained)
- Request timeout is set to 120 seconds to accommodate large files and model inference time
- All services use bridge networking for inter-service communication
