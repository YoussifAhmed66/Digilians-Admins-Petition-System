FROM python:3.11-slim

# Install LibreOffice (needed for DOCX -> PDF conversion)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libreoffice-writer \
    fonts-liberation \
    fonts-noto-cjk \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first (layer cache optimization)
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/app ./app
COPY frontend ./frontend
COPY docs ./docs

# Set pythonpath to allow absolute imports
ENV PYTHONPATH=/app

# Cloud Run injects PORT at runtime (default 8080); fallback to 8000 locally
ENV PORT=8080

EXPOSE 8080

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
