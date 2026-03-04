# Indian Railways Health Index (RHI)

Production-grade monitoring system for Indian Railways train health assessment using AI and real-time sensor analysis.

## 🚀 Quick Start

### Using Docker (Recommended)

```bash
# Windows
start.bat

# Mac/Linux
bash start.sh

# Or manually
docker-compose up --build
```

All services start automatically:
- **Frontend:** http://localhost:8000 (admin/admin123)
- **Backend API:** http://localhost:8001
- **API Docs:** http://localhost:8001/docs
- **Dagster Pipeline UI:** http://localhost:3000

### Without Docker

```bash
# Frontend
cd TrainHealthIndex && python -m http.server 8000

# Backend (in new terminal)
cd backend && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt && python main.py

# Pipeline (in new terminal)
cd pipeline && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt && dagit -f main.py
```

## ✨ Features

### Frontend Dashboard
- ✅ Login with credentials (admin/admin123)
- ✅ Real-time sensor data visualization
- ✅ Electronic THI calculation every 5 seconds
- ✅ Train search with autocomplete
- ✅ Favorites management
- ✅ Route mapping
- ✅ Maintenance recommendations
- ✅ Export reports (JSON)

### Backend API
- ✅ Train information retrieval by train number
- ✅ Single-point THI generation with sensor data
- ✅ List all trains with pagination
- ✅ Health monitoring
- ✅ CORS support for frontend
- ✅ Interactive API documentation

### Dagster Pipeline UI
- ✅ Visual pipeline editor and execution
- ✅ Sensor data generation (100 records)
- ✅ Data validation and quality checks
- ✅ CSV export with timestamps
- ✅ Job execution history
- ✅ Real-time logs and monitoring

## 📊 Sensor Parameters

| Parameter | Range | Unit |
|-----------|-------|------|
| Brake Temperature | 30-120 | °C |
| Axle Vibration | 0.1-4.0 | mm/s |
| Wheel Wear | 10-90 | % |
| Engine Load | 40-100 | % |
| Battery Voltage | 10.5-14.5 | V |
| Fuel Efficiency | 2-5 | km/L |

## 🎯 THI Scoring

- **80-100:** ✅ Excellent (Routine checks)
- **50-79:** ⚠️ Caution (48-hour maintenance)
- **0-49:** ❌ Critical (Immediate inspection)

## 📂 Project Structure

```
THI/
├── docker-compose.yml          # Service orchestration
├── nginx.conf                  # Frontend proxy config
├── DEPLOYMENT_GUIDE.md         # Detailed documentation
├── start.bat / start.sh        # Quick start scripts
├── TrainHealthIndex/
│   └── index.html              # Frontend application
├── backend/
│   ├── main.py                 # FastAPI server
│   ├── train_data.json         # Train data (copied from frontend)
│   ├── Dockerfile
│   └── requirements.txt
├── pipeline/
│   ├── main.py                 # Dagster pipeline definition
│   ├── dagster.yaml            # Dagster configuration
│   ├── entrypoint.sh           # Pipeline startup script
│   ├── Dockerfile
│   └── requirements.txt
├── sensor_data/                # Generated CSV files
└── README.md                   # This file
```

## 🔌 API Endpoints

```
GET  /               → API info
GET  /get-train/{train_no}    → Train details (e.g., /get-train/10103)
POST /generate-thi   → Generate THI score
GET  /list-trains    → All trains (paginated)
GET  /health         → Service health
GET  /docs           → Interactive documentation
```

## 📍 Services & Login

| Service | URL | Credentials |
|---------|-----|-------------|
| **Frontend** | http://localhost:8000 | admin / admin123 |
| **Backend API** | http://localhost:8001 | No auth needed |
| **API Documentation** | http://localhost:8001/docs | Interactive testing |
| **Dagster Pipeline** | http://localhost:3000 | No auth needed |

## 🐳 Docker Commands

```bash
# Start all services
docker-compose up --build

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f pipeline
```

## 🧪 Test Endpoints

### Get Train Info
```bash
curl http://localhost:8001/get-train/10103
```

### Generate THI
```bash
curl -X POST http://localhost:8001/generate-thi?train_no=10103
```

### List Trains (with pagination)
```bash
curl http://localhost:8001/list-trains?skip=0&limit=5
```

### Health Check
```bash
curl http://localhost:8001/health
```

## 📋 Requirements

- Docker & Docker Compose
- 4GB+ RAM recommended
- Ports 8000, 8001, 3000 available

## 🔧 Configuration

Copy `.env.example` to `.env` for environment variables:

```bash
cp .env.example .env
```

## 📚 Documentation

For detailed information, see [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

## 🛠️ Development

**Backend Development:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

**Pipeline Development:**
```bash
cd pipeline
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
dagit -f main.py
```

## 📊 Output Files

Generated sensor data CSV available in `sensor_data/` folder:
```
sensor_data_20240115_103045.csv
```

## ✅ Status Checks

- Frontend health: http://localhost:8000/
- Backend health: http://localhost:8001/health
- Dagster UI: http://localhost:3000/
- All services: `docker-compose logs`

## 🚨 Troubleshooting

**Port in use?**
```bash
# Windows
netstat -ano | findstr :8000

# Mac/Linux
lsof -i :8000
```

**Docker not found?**
Install Docker Desktop from https://www.docker.com/products/docker-desktop

**Backend API not responding?**
```bash
# Check backend logs
docker-compose logs backend

# Verify JSON file is present
docker-compose exec backend ls -la /app/train_data.json
```

**Dagster UI not loading?**
```bash
# Check pipeline logs
docker-compose logs pipeline

# Restart pipeline
docker-compose restart pipeline
```

## 📞 Support

- API Documentation: http://localhost:8001/docs
- Dagster Docs: https://docs.dagster.io/
- Check logs: `docker-compose logs -f`
- Verify containers: `docker ps`

---

**Version:** 1.0.0 | **Status:** Production Ready | **Last Updated:** January 2024

