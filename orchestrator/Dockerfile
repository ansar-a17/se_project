FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Copy dependency list
COPY requirements.txt .

# Install Python dependencies without caching
RUN pip install --no-cache-dir -r requirements.txt

# Copy main orchestrator script
COPY orchestrator.py .

# Create a temporary directory (used by some processing tasks)
RUN mkdir -p /tmp

# Expose FastAPI port
EXPOSE 5000

# Container health check: calls /health every 30s
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/health')"

CMD ["python", "orchestrator.py"]
