# Use official Python image as base
FROM python:3.11.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Create and switch to non-root user
RUN useradd -m appuser
RUN chown -R appuser:appuser /home/appuser && chmod u+w /home/appuser

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt requirements.txt

# Install dependencies
RUN pip3 install --upgrade pip
RUN pip3 install --no-cache-dir -v -r requirements.txt

# Copy application code
COPY . .

# Change ownership to non-root user
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8089

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8089/ || exit 1

# Set entrypoint and command
ENTRYPOINT ["chainlit"]
CMD ["run", "app.py", "--host", "0.0.0.0", "--port", "8089"]