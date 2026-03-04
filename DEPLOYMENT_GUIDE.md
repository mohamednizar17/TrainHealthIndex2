# Indian Railways Health Index - Production Deployment Guide

## Overview

This is a production-grade monitoring system for the Indian Railways Health Index (THI) comprising three interconnected services:

1. **Frontend** - Interactive web dashboard with real-time monitoring
2. **Backend API** - RESTful API for train data and THI calculation
3. **Data Pipeline** - Automated sensor data generation and processing

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Environment                        │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────┐   ┌──────────────────┐                │
│  │    Frontend      │   │  Backend API     │                │
│  │  (Nginx)         │◄─►│  (FastAPI)       │                │
│  │  Port 8000       │   │  Port 8001       │                │
│  └──────────────────┘   └──────────────────┘                │
│                                                               │
│  ┌──────────────────────────────────────┐                   │
│  │  Pipeline (Dagster)                  │                   │
│  │  Generates Sensor Data → CSV Export  │                   │
│  └──────────────────────────────────────┘                   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites

- Docker & Docker Compose installed
- Windows/Mac/Linux with 2+ GB RAM
- Port 8000 and 8001 available

### Run All Services

```bash
# Navigate to project directory
cd THI

# Start all services
docker-compose up --build

# Wait for all services to start (30-60 seconds)
```

### Access Services

| Service | URL | Purpose |
|---------|-----|---------|
| **Frontend** | http://localhost:8000 | Web Dashboard |
| **Backend API** | http://localhost:8001 | REST API |
| **API Docs** | http://localhost:8001/docs | Interactive API Documentation |

### Frontend Login

```
Username: admin
Password: admin123
```

## Service Details

### 1. Frontend (Nginx)

**Port:** 8000

**Features:**
- Login page with predefined credentials
- Real-time sensor data visualization
- Train health index calculation
- Route mapping and schedule display
- Responsive UI (mobile-friendly)

**Files:**
- `TrainHealthIndex/index.html` - Main dashboard

**Key Functions:**
- Continuous sensor data generation (5-second intervals)
- Real-time THI calculation and updates
- Train favorites management
- Export reports in JSON format

### 2. Backend (FastAPI)

**Port:** 8001

**Features:**
- RESTful API endpoints
- Train data retrieval from JSON
- Single-point THI generation with sensor data
- Health monitoring
- CORS-enabled for cross-origin requests

**Key Endpoints:**

```bash
# Get API Information
GET http://localhost:8001/

# Get Train Information
GET http://localhost:8001/get-train/{train_no}

# Generate THI Score (generates sensor data internally)
POST http://localhost:8001/generate-thi?train_no=10103

# List All Trains
GET http://localhost:8001/list-trains?skip=0&limit=10

# Health Check
GET http://localhost:8001/health

# API Documentation
GET http://localhost:8001/docs
```

**Example API Request:**

```bash
curl -X POST http://localhost:8001/generate-thi?train_no=10103
```

**Response:**
```json
{
  "train_no": 10103,
  "timestamp": "2024-01-15T10:30:45.123456",
  "sensor_data": {
    "Brake Temperature (°C)": 65.34,
    "Axle Vibration (mm/s)": 1.68,
    "Wheel Wear (%)": 33.99,
    "Engine Load (%)": 58.24,
    "Battery Voltage (V)": 11.05,
    "Fuel Efficiency (km/L)": 4.19
  },
  "thi_score": 100,
  "maintenance_suggestion": "✅ Train in excellent condition. Routine checks sufficient."
}
```

### 3. Pipeline (Dagster)

**Purpose:** Generate synthetic sensor data for analytics

**Output:** CSV file with 100 sensor records

**Features:**
- Automated sensor data generation
- Data validation and quality checks
- Timestamped records for tracking
- Summary statistics

**Generated CSV Structure:**

```
Train_Number | Timestamp | Brake_Temperature_C | Axle_Vibration_mms | Wheel_Wear_Percent | Engine_Load_Percent | Battery_Voltage_V | Fuel_Efficiency_kmL
```

**Output Location:** `sensor_data/sensor_data_YYYYMMDD_HHMMSS.csv`

## Sensor Data Schema

### Parameters Generated

| Parameter | Range | Unit | Typical Threshold |
|-----------|-------|------|------------------|
| Brake Temperature | 30-120 | °C | < 90 (good) |
| Axle Vibration | 0.1-4.0 | mm/s | < 2.5 (good) |
| Wheel Wear | 10-90 | % | < 70 (good) |
| Engine Load | 40-100 | % | < 85 (good) |
| Battery Voltage | 10.5-14.5 | V | ≥ 11 (good) |
| Fuel Efficiency | 2-5 | km/L | ≥ 3 (good) |

## THI Scoring Algorithm

**Starting Score:** 100 points

**Deductions:**
- Brake Temp > 90°C: -15 points
- Axle Vibration > 2.5 mm/s: -20 points
- Wheel Wear > 70%: -25 points
- Engine Load > 85%: -10 points
- Battery Voltage < 11V: -10 points
- Fuel Efficiency < 3 km/L: -10 points

**Thresholds:**
- **80-100:** ✅ Excellent - Routine checks sufficient
- **50-79:** ⚠️ Caution - Schedule maintenance within 48 hours
- **0-49:** ❌ Critical - Immediate inspection required

## File Structure

```
THI/
├── docker-compose.yml          # Orchestration configuration
├── nginx.conf                  # Frontend server configuration
├── TrainHealthIndex/
│   ├── index.html              # Frontend dashboard
│   ├── train_max_distance_only.json  # Train data
│   ├── start_server.bat        # Legacy local server
│   └── SETUP_GUIDE.md          # Original setup guide
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── requirements.txt        # Python dependencies
│   └── Dockerfile              # Container configuration
├── pipeline/
│   ├── main.py                 # Dagster pipeline
│   ├── requirements.txt        # Python dependencies
│   └── Dockerfile              # Container configuration
└── sensor_data/                # Generated CSV files
```

## Environment Variables

### Backend
- `PYTHONUNBUFFERED=1` - Unbuffered Python output
- `FASTAPI_HOST=0.0.0.0` - API host
- `FASTAPI_PORT=8001` - API port

### Pipeline
- `PYTHONUNBUFFERED=1` - Unbuffered Python output

## Docker Commands

```bash
# Start all services
docker-compose up --build

# Start in background
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f pipeline

# Rebuild services
docker-compose build --no-cache

# Remove all containers
docker-compose down -v
```

## Local Development (Without Docker)

### Frontend
```bash
cd TrainHealthIndex
python -m http.server 8000
# Access at http://localhost:8000
```

### Backend
```bash
cd backend
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate
pip install -r requirements.txt
python main.py
# API available at http://localhost:8001
```

### Pipeline
```bash
cd pipeline
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

## API Integration Examples

### Python
```python
import requests

# Generate THI for train 10103
response = requests.post('http://localhost:8001/generate-thi?train_no=10103')
data = response.json()
print(f"THI Score: {data['thi_score']}")
print(f"Timestamp: {data['timestamp']}")

# Get train info
response = requests.get('http://localhost:8001/get-train/10103')
train = response.json()
print(f"Train: {train['train_name']}")
```

### JavaScript
```javascript
// Generate THI
fetch('http://localhost:8001/generate-thi?train_no=10103', {
    method: 'POST'
})
.then(response => response.json())
.then(data => {
    console.log('THI Score:', data.thi_score);
    console.log('Timestamp:', data.timestamp);
});

// Get train info
fetch('http://localhost:8001/get-train/10103')
.then(response => response.json())
.then(train => console.log('Train:', train.train_name));
```

### cURL
```bash
# Generate THI
curl -X POST http://localhost:8001/generate-thi?train_no=10103

# Get train info
curl http://localhost:8001/get-train/10103

# List trains
curl http://localhost:8001/list-trains?skip=0&limit=5
```

## Production Deployment Considerations

### Performance Optimization
- Use container orchestration (Kubernetes) for scaling
- Implement caching layer (Redis) for API responses
- Add database (PostgreSQL) for persistent storage
- Implement monitoring (Prometheus, Grafana)

### Security Hardening
- Replace demo credentials with OAuth/JWT
- Implement rate limiting (already in Nginx)
- Add SSL/TLS certificates
- Use environment variables for secrets
- Implement API authentication

### Monitoring
- Container health checks configured
- Log aggregation recommended
- Metrics collection for performance analysis

## Troubleshooting

### Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000
# Kill process
kill -9 <PID>
```

### Backend Connection Failed
```bash
# Check backend status
docker-compose logs backend

# Restart backend
docker-compose restart backend
```

### CSV Not Generated
```bash
# Check pipeline logs
docker-compose logs pipeline

# Verify sensor_data directory exists
ls -la sensor_data/
```

### CORS Issues
- Nginx config includes proper CORS headers
- Frontend can communicate with backend via proxy

## Support & Documentation

- **API Documentation:** http://localhost:8001/docs
- **Interactive API Testing:** http://localhost:8001/docs (Swagger UI)
- **Backend Endpoint Reference:** See Service Details section above

## Version Information

- **FastAPI:** 0.104.1
- **Dagster:** 1.5.0
- **Python:** 3.11
- **Pandas:** 2.1.3
- **Nginx:** Latest Alpine

## Next Steps

1. ✅ Start Docker Compose: `docker-compose up --build`
2. ✅ Login to frontend: http://localhost:8000 (admin/admin123)
3. ✅ Test API: http://localhost:8001/docs
4. ✅ Monitor pipeline: `docker-compose logs pipeline`

---

**Status:** Production Ready | **Last Updated:** January 2024
