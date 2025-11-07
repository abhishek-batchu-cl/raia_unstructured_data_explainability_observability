FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy RAIA SDK (in production, install from package)
COPY ../../sdk/python/raia /app/raia

# Copy application code
COPY main.py .

# Copy schemas
COPY ../../schemas /app/schemas

# Create data directory
RUN mkdir -p /data

# Non-root user for security
RUN useradd -m -u 1000 raia && chown -R raia:raia /app /data
USER raia

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/healthz')"

# Run service
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
