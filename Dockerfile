# Dockerfile
FROM mcr.microsoft.com/playwright/python:v1.55.0-jammy

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt .
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

# Set Python path to include src directory
ENV PYTHONPATH=/app/src

# Default entry point for CLI
ENTRYPOINT ["python", "-m", "src.cli.main"]
