# Use official Python image as base
# FROM python:3.11-slim-ubuntu (it works as well)
FROM ubuntu:20.04

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Install Python 3.11
RUN apt-get update && apt-get install -y software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt-get update && apt-get install -y python3.11 python3.11-distutils
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
RUN update-alternatives --set python3 /usr/bin/python3.11

# Install pip
RUN apt-get install -y curl
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python3.11 get-pip.py
RUN apt-get update && apt-get install -y python3-setuptools python3-dev

# Create and switch to non-root user
RUN useradd -m appuser
RUN chown -R appuser:appuser /home/appuser && chmod u+w /home/appuser

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    libstdc++6 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt requirements.txt

# Install Python dependencies with specific order
RUN pip3 install --upgrade pip setuptools wheel
RUN pip3 install torch transformers --no-cache-dir
RUN pip3 install --no-cache-dir -r requirements.txt

# Configure guardrails and install hub packages
RUN guardrails configure --enable-metrics --enable-remote-inferencing --token "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJnb29nbGUtb2F1dGgyfDEwNDk5NjYzODU5NDM1MTEyNzA3MSIsImFwaUtleUlkIjoiZGY3ZjI2NWItN2M4ZS00MmZiLTgzOGMtZTY0OTNhYjk1MjA2Iiwic2NvcGUiOiJyZWFkOnBhY2thZ2VzIiwicGVybWlzc2lvbnMiOltdLCJpYXQiOjE3MzkzMTkyMDMsImV4cCI6NDg5MjkxOTIwM30.QKdst-gnohB35Nms6LhegIUoTu4YbIopukGnqwZpE90"

# Install hub packages one by one with error handling
RUN guardrails hub install hub://guardrails/detect_pii || exit 1
RUN guardrails hub install hub://guardrails/secrets_present || exit 1
RUN guardrails hub install hub://guardrails/similar_to_document || exit 1
RUN guardrails hub install hub://guardrails/web_sanitization || exit 1

# Copy application code
COPY . .

# Change ownership to non-root user
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8088

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8088/ || exit 1

# Create an entrypoint script
RUN echo '#!/bin/bash\n\
guardrails configure --enable-metrics --enable-remote-inferencing --token "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJnb29nbGUtb2F1dGgyfDEwNDk5NjYzODU5NDM1MTEyNzA3MSIsImFwaUtleUlkIjoiZGY3ZjI2NWItN2M4ZS00MmZiLTgzOGMtZTY0OTNhYjk1MjA2Iiwic2NvcGUiOiJyZWFkOnBhY2thZ2VzIiwicGVybWlzc2lvbnMiOltdLCJpYXQiOjE3MzkzMTkyMDMsImV4cCI6NDg5MjkxOTIwM30.QKdst-gnohB35Nms6LhegIUoTu4YbIopukGnqwZpE90"\n\
chainlit run app.py --host 0.0.0.0 --port 8088' > /app/entrypoint.sh && \
    chmod +x /app/entrypoint.sh

# Set the new entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]
# CMD ["run", "app.py", "--host", "0.0.0.0", "--port", "8088"]