# Translation Service

A FastAPI microservice for English to Dutch translation using the Helsinki-NLP MarianMT model.

## Features

- **FastAPI REST API** for translation
- **English to Dutch** translation
- **Health check** endpoint
- Compatible with modern Python 3.11+ and PyTorch 2.6+
- Optimized for production with Docker support

## API Endpoints

### GET `/`
Health check and service information.

**Response:**
```json
{
  "service": "Translation Service",
  "status": "running",
  "model": "Helsinki-NLP/opus-mt-en-nl",
  "source_language": "English",
  "target_language": "Dutch"
}
```

### POST `/translate`
Translate English text to Dutch.

**Request:**
```json
{
  "text": "Hello, how are you today?",
  "source_lang": "en",
  "target_lang": "nl"
}
```

**Response:**
```json
{
  "original_text": "Hello, how are you today?",
  "translated_text": "Hallo, hoe gaat het vandaag?",
  "source_lang": "en",
  "target_lang": "nl"
}
```

### GET `/health`
Service health check.

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true
}
```

## Running Locally

### Prerequisites
- Python 3.11+
- Virtual environment (recommended)

### Installation

```powershell
# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the service
python translation.py
```

The service will be available at `http://localhost:8003`

### Testing

```powershell
# Test with PowerShell
$body = @{
    text = "Hello, how are you?"
    source_lang = "en"
    target_lang = "nl"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8003/translate" `
    -Method POST `
    -Body $body `
    -ContentType "application/json"
```

```bash
# Test with curl (Git Bash or WSL)
curl -X POST "http://localhost:8003/translate" \
    -H "Content-Type: application/json" \
    -d '{"text": "Hello, how are you?", "source_lang": "en", "target_lang": "nl"}'
```

## Running with Docker

### Build the image

```bash
docker build -t translation-service .
```

### Run the container

```bash
docker run -p 8003:8003 translation-service
```

## Running with Docker Compose

The translation service is integrated into the main docker-compose.yml:

```bash
# From the project root
docker-compose up translation
```

Or start all services:

```bash
docker-compose up
```

## Integration with Orchestrator

The translation service is automatically integrated with the orchestrator. To use translation in your workflow:

```bash
# Without translation (default)
POST /process_screenshot
  - file: <image file>

# With translation (English -> Dutch)
POST /process_screenshot?translate=true
  - file: <image file>
```

When `translate=true`, the workflow becomes:
1. Image → Text (English)
2. Text → Translation (Dutch)
3. Text → Speech (Dutch audio)

## Model Information

- **Model**: [Helsinki-NLP/opus-mt-en-nl](https://huggingface.co/Helsinki-NLP/opus-mt-en-nl)
- **Framework**: Transformers (Hugging Face)
- **Architecture**: MarianMT
- **Language Pair**: English → Dutch
- **License**: Apache 2.0

## Performance

- **First request**: ~2-3 seconds (model loading on first use)
- **Subsequent requests**: ~100-200ms per translation
- **Max input length**: 512 tokens
- **Batch processing**: Supported

## Environment Variables

- `PORT`: Service port (default: 8003)
- `HOST`: Service host (default: 0.0.0.0)

## Error Handling

The service returns appropriate HTTP status codes:

- `200`: Success
- `400`: Invalid request (empty text, unsupported language pair)
- `500`: Internal server error (model failure)

## Notes

- Currently only supports English to Dutch (en→nl)
- Text is automatically truncated to 512 tokens
- The model is loaded on application startup
- Recommended: Install `sacremoses` for better tokenization (optional)

## Future Enhancements

- Support for additional language pairs
- Batch translation endpoint
- Model caching for faster startup
- Custom model support
- Translation quality scoring
