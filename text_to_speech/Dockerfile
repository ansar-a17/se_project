FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY text_to_speech/requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu

RUN pip install --no-cache-dir -r requirements.txt

COPY text_to_speech/text_to_speech.py .

RUN mkdir -p /app/audio_files

EXPOSE 7999

ENV PYTHONUNBUFFERED=1

CMD ["python", "text_to_speech.py"]
