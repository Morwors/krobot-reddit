FROM python:3.11-slim

WORKDIR /app

# Install runtime deps + build deps for PyAV (av==11.* required by faster-whisper)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsndfile1 \
    espeak-ng \
    git \
    fonts-liberation \
    fonts-dejavu-core \
    pkg-config \
    gcc \
    libavcodec-dev \
    libavformat-dev \
    libavutil-dev \
    libavdevice-dev \
    libavfilter-dev \
    libswscale-dev \
    libswresample-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# Pin av==11.4.2 explicitly to avoid TTS pulling a different version
RUN pip install --no-cache-dir av==11.4.2 && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/storage/backgrounds /app/storage/logos /app/storage/output /app/storage/temp

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
