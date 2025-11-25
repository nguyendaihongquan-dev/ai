FROM python:3.11-slim

# Prevents Python from writing .pyc files and ensures unbuffered logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    VIDEOMAE_MODEL_PATH=/models/videomae_finetuned_final

WORKDIR /app

# Install system dependencies required by av/opencv
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Copy dependency list and install
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy application source
COPY . /app

# Directory to mount fine-tuned model weights at runtime
RUN mkdir -p /models
VOLUME ["/models"]

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]

