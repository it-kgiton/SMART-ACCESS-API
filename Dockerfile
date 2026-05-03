FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    g++ \
    python3-dev \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# NOTE: InsightFace buffalo_l models (~300MB) are downloaded at container startup
# via biometric_engine.initialize() which runs in background (non-blocking).
# API is fully functional immediately; biometric features ready after ~60s on first boot.

COPY . .

# PORT is injected by Railway at runtime; default to 8000 for local use
EXPOSE 8000

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
