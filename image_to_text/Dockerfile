FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Install system dependencies needed for image processing and PyTorch CPU
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies file
COPY image_to_text/requirements.txt .

# Upgrade pip and install PyTorch (CPU-only build)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Install project dependencies
RUN pip install --no-cache-dir -r requirements.txt

COPY image_to_text/image_to_text.py .

# Expose API port
EXPOSE 8000

ENV PYTHONUNBUFFERED=1

CMD ["python", "image_to_text.py"]
