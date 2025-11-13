# RAIA Unified Library - Docker Image
# Complete production-grade instrumentation and evaluation framework
# Compatible with Mac (Intel/Apple Silicon), Windows, Linux

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy the unified raia package
COPY raia/ /app/raia/
COPY setup.py /app/
COPY pyproject.toml /app/
COPY README.md /app/
COPY LICENSE /app/ 2>/dev/null || true

# Install Python dependencies and the unified raia package
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e /app

# Install development dependencies for testing
RUN pip install --no-cache-dir \
    pytest>=7.0.0 \
    pytest-asyncio>=0.21.0 \
    pytest-cov>=4.0.0

# Install optional dependencies for examples
RUN pip install --no-cache-dir \
    langchain>=0.1.0 \
    langchain-core>=0.1.0 \
    langgraph>=0.0.20 || true

# Create directories for data and logs
RUN mkdir -p /app/data /app/logs /app/output

# Set Python path
ENV PYTHONPATH=/app:$PYTHONPATH

# Expose ports (if needed for services)
EXPOSE 8000

# Default command - verify installation
CMD ["python", "-c", "import raia; print('✅ RAIA Unified Library ready!'); print(f'Version: {raia.__version__}'); print('Event Logging + Inspectors available')"]
