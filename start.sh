#!/bin/bash

# Indian Railways Health Index - Quick Start Script
# This script automates the startup of all services

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  Indian Railways Health Index - Production Deployment      ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from template..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✅ .env file created from .env.example"
    fi
fi

echo ""
echo "Starting Indian Railways Health Index..."
echo "═════════════════════════════════════════"
echo ""

# Build and start services
docker-compose up --build

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                    Startup Complete!                       ║"
echo "╠════════════════════════════════════════════════════════════╣"
echo "║                                                            ║"
echo "║  Frontend Dashboard:  http://localhost:8000               ║"
echo "║  Backend API:         http://localhost:8001               ║"
echo "║  API Documentation:   http://localhost:8001/docs          ║"
echo "║  Dagster Pipeline UI: http://localhost:3000              ║"
echo "║                                                            ║"
echo "║  Frontend Login Credentials:                              ║"
echo "║  - Username: admin                                        ║"
echo "║  - Password: admin123                                     ║"
echo "║                                                            ║"
echo "║  Generated Files:     ./sensor_data/                      ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"

