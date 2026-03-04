#!/bin/bash
# Pipeline entrypoint script
# Sets up Dagster environment and starts the UI

set -e

# Create necessary directories
mkdir -p /app/dagster_home/runs
mkdir -p /app/dagster_home/storage
mkdir -p /app/dagster_home/logs
mkdir -p /app/dagster_home/schedules
mkdir -p /app/sensor_data

echo "✅ Directories created"

# Start Dagit (Dagster UI)
echo "🚀 Starting Dagster UI on port 3000..."
echo "   Dashboard: http://localhost:3000"

# Run both the UI and keep the container alive
dagit -h 0.0.0.0 -p 3000 -f main.py
