FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Install audio dependencies required for TTS models
RUN apt-get update && apt-get install -y \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependency list
COPY text_to_speech/requirements.txt .

# Install pip, PyTorch CPU wheel, and project dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu

RUN pip install --no-cache-dir -r requirements.txt

# Copy the TTS service script
COPY text_to_speech/text_to_speech.py .

RUN mkdir -p /app/audio_files

# Expose port for the TTS service
EXPOSE 7999

ENV PYTHONUNBUFFERED=1

CMD ["python", "text_to_speech.py"]
