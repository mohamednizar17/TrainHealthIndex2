@echo off
REM Indian Railways Health Index - Quick Start Script (Windows)

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║  Indian Railways Health Index - Production Deployment      ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not installed. Please install Docker Desktop first.
    pause
    exit /b 1
)

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose is not installed. Please install Docker Desktop first.
    pause
    exit /b 1
)

echo ✅ Docker and Docker Compose are installed
echo.

REM Check if .env file exists
if not exist .env (
    echo ⚠️  .env file not found. Creating from template...
    if exist .env.example (
        copy .env.example .env
        echo ✅ .env file created from .env.example
    )
)

echo.
echo Starting Indian Railways Health Index...
echo ═════════════════════════════════════════
echo.

REM Build and start services
docker-compose up --build

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                    Startup Complete!                       ║
echo ╠════════════════════════════════════════════════════════════╣
echo ║                                                            ║
echo ║  Frontend Dashboard:  http://localhost:8000               ║
echo ║  Backend API:         http://localhost:8001               ║
echo ║  API Documentation:   http://localhost:8001/docs          ║
echo ║  Dagster Pipeline UI: http://localhost:3000              ║
echo ║                                                            ║
echo ║  Frontend Login Credentials:                              ║
echo ║  - Username: admin                                        ║
echo ║  - Password: admin123                                     ║
echo ║                                                            ║
echo ║  Generated Files:     .\sensor_data\                      ║
echo ║                                                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
pause

