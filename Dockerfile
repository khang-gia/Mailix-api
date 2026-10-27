FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies required for psycopg2, pillow, and openpyxl
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Ensure log and media directories exist
RUN mkdir -p /app/logs /app/media /app/staticfiles

EXPOSE 8000

# Default command: ASGI application via Gunicorn + Uvicorn worker
CMD ["gunicorn", "tttmail.asgi:application", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "300", "--capture-output"]
