FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ffmpeg \
        fontconfig \
        wget \
        curl \
        ca-certificates \
        && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Create necessary directories
RUN mkdir -p fonts downloads database

# Copy font files first (if they exist)
COPY fonts/ /app/fonts/

# Register custom fonts with the system
RUN fc-cache -fv

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . /app/

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set proper permissions
RUN chown -R appuser:appuser /app && \
    chmod -R 755 /app/fonts && \
    chmod -R 755 /app/downloads

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('https://api.telegram.org')" || exit 1

# Expose port (if needed for webhooks)
EXPOSE 8080

# Set default command
CMD ["python", "muxbot.py"]
