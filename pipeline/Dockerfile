# Pipeline Dockerfile - Dagster UI
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Create and activate virtual environment, install dependencies
RUN python -m venv /opt/venv && \
    . /opt/venv/bin/activate && \
    pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy application and configuration
COPY main.py .
COPY dagster.yaml .
COPY entrypoint.sh .

# Make entrypoint executable
RUN chmod +x /app/entrypoint.sh

# Set environment to use venv
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV DAGSTER_HOME=/app/dagster_home

# Create necessary directories
RUN mkdir -p /app/dagster_home/runs \
    && mkdir -p /app/dagster_home/storage \
    && mkdir -p /app/dagster_home/logs \
    && mkdir -p /app/dagster_home/schedules \
    && mkdir -p /app/sensor_data

# Expose Dagster UI port
EXPOSE 3000

# Health check for UI
HEALTHCHECK --interval=10s --timeout=5s --retries=3 --start-period=30s \
    CMD curl -f http://localhost:3000 || exit 1

# Run entrypoint
CMD ["/app/entrypoint.sh"]

