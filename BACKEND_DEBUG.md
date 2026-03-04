# Backend API Debugging & Testing Guide

## 🔧 Quick Diagnosis

### File Verification
```bash
# Windows - Check JSON file exists
Test-Path "c:\Users\nizar\Desktop\THI\backend\train_data.json"
# Should return: True

# Check file size (should be ~2.5MB)
Get-Item "c:\Users\nizar\Desktop\THI\backend\train_data.json" | Select Length
```

---

## 🚀 Running Everything Fresh

### Option 1: Docker (Recommended)
```bash
cd c:\Users\nizar\Desktop\THI
start.bat
```

**Wait 30-60 seconds for services to start**, then test:
```bash
curl http://localhost:8001/health
curl http://localhost:8001/list-trains?skip=0&limit=3
curl http://localhost:8001/get-train/10103
```

### Option 2: Local Development (Backend Only)
```bash
cd c:\Users\nizar\Desktop\THI\backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

You should see output like:
```
======================================================================
STARTING INDIAN RAILWAYS HEALTH INDEX BACKEND
======================================================================

📂 Searching for train data file...
   Current working directory: c:\Users\nizar\Desktop\THI\backend

   Checking 5 possible locations:
   1. c:\Users\nizar\Desktop\THI\backend\train_data.json [✅ EXISTS]
   
   🔄 Loading from: c:\Users\nizar\Desktop\THI\backend\train_data.json
   ✅ Successfully loaded 97563 train records
   
   📊 Sample records:
      - Train 10103: MANDOVI EXPR
      - Train 10104: MANDOVI EXPR

📊 DATA STATUS:
   ✅ Total records loaded: 97563
   ✅ Unique trains: 5821

======================================================================
✅ Backend initialized successfully
======================================================================

🚀 BACKEND STARTUP STATUS
======================================================================
✅ API Server running on http://0.0.0.0:8001
📊 Train records available: 97563
🚂 Unique trains: 5821
📚 API Documentation: http://localhost:8001/docs
======================================================================
```

---

## 🧪 Testing the API

### Test 1: Health Check
```bash
curl http://localhost:8001/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:45.123456",
  "trains_in_database": 5821
}
```

**Console Output:**
```
No special logging for health check
```

---

### Test 2: List Trains
```bash
curl http://localhost:8001/list-trains?skip=0&limit=3
```

**Expected Response:**
```json
{
  "total": 5821,
  "skip": 0,
  "limit": 3,
  "trains": [
    {
      "train_no": 10103,
      "train_name": "MANDOVI EXPR",
      "source": "CSMT - CST-MUMBAI",
      "destination": "MAO - MADGOAN JN.",
      "distance": 590.0
    },
    ...
  ]
}
```

**Console Output:**
```
📋 GET /list-trains?skip=0&limit=3
   Total records in DB: 97563
   ✅ Total unique trains: 5821
   ✅ Returning: 3 trains
```

---

### Test 3: Get Specific Train
```bash
curl http://localhost:8001/get-train/10103
```

**Expected Response:**
```json
{
  "train_no": 10103,
  "train_name": "MANDOVI EXPR",
  "source_station": "CSMT",
  "source_station_name": "CST-MUMBAI",
  "destination_station": "MAO",
  "destination_station_name": "MADGOAN JN.",
  "distance": 590.0
}
```

**Console Output:**
```
🔍 GET /get-train/10103
   Total records in DB: 97563
   ✅ Found: MANDOVI EXPR
```

---

### Test 4: Generate THI
```bash
curl -X POST http://localhost:8001/generate-thi?train_no=10103
```

**Expected Response:**
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

---

## 📊 Common Issues & Solutions

### Issue 1: Database Empty Error
**Problem:**
```json
{
  "detail": "Train database is empty. Check if JSON file loaded correctly."
}
```

**Solution:**
1. Check file exists: `Test-Path c:\Users\nizar\Desktop\THI\backend\train_data.json`
2. Check file size: `(Get-Item ...).Length` (should be ~2.5MB)
3. Rebuild Docker: `docker-compose build --no-cache backend`
4. Restart backend: `docker-compose restart backend`

---

### Issue 2: Train Not Found
**Problem:**
```json
{
  "detail": "Train 99999 not found in database. Available: [10103, 10104, ...]"
}
```

**Solution:**
- Use a valid train number from the database
- Test with: `curl http://localhost:8001/get-train/10103`

---

### Issue 3: Connection Refused
**Problem:**
```
curl: (7) Failed to connect to localhost port 8001: Connection refused
```

**Solution:**
```bash
# Check if backend is running
docker ps | findstr backend

# Check backend logs
docker-compose logs backend

# Restart
docker-compose restart backend
```

---

### Issue 4: Pendulum Error
**Problem:**
```
AttributeError: Pendulum. Did you mean: '_pendulum'?
```

**Solution:**
This is fixed! Updated requirements to Dagster 1.7.0 which resolves dependency conflicts.
```bash
# Rebuild Docker
docker-compose down
docker-compose build --no-cache
docker-compose up
```

---

## 🔍 Advanced Debugging

### Check Docker Logs
```bash
# All services
docker-compose logs -f

# Just backend
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100 backend
```

### Execute Commands in Container
```bash
# Check file exists in container
docker-compose exec backend ls -la /app/train_data.json

# Test Python import
docker-compose exec backend python -c "import json; print('✅ JSON module works')"

# Test file parsing
docker-compose exec backend python -c "
import json
with open('/app/train_data.json') as f:
    data = json.load(f)
    print(f'✅ Loaded {len(data)} records')
"
```

### Python Testing Script
```bash
# From THI directory, run test script
cd c:\Users\nizar\Desktop\THI
python test_api.py
```

This will test all endpoints and show which ones work.

---

## 📚 API Documentation

### Interactive Swagger UI
Open in browser: `http://localhost:8001/docs`

This shows:
- All available endpoints
- Request/response schemas
- Try endpoints directly in browser
- Download API spec

---

## ✅ Verification Checklist

- [ ] JSON file exists at `backend/train_data.json` (~2.5MB)
- [ ] Docker backend container is running: `docker ps | findstr backend`
- [ ] Backend logs show "✅ Successfully loaded" message
- [ ] Health endpoint returns 200: `curl http://localhost:8001/health`
- [ ] List trains returns data: `curl http://localhost:8001/list-trains`
- [ ] Get train returns data: `curl http://localhost:8001/get-train/10103`
- [ ] Generate THI works: `curl -X POST http://localhost:8001/generate-thi`

---

## 📝 Next Steps

1. Run `start.bat` or `docker-compose up --build`
2. Wait for "✅ Backend initialized successfully" message
3. Test endpoints using provided commands
4. Use `http://localhost:8001/docs` for interactive testing
5. Check `docker-compose logs backend` if issues occur

---

## 🆘 Still Having Issues?

1. **Check logs**: `docker-compose logs backend`
2. **What get printed?** Backend prints when files are found/loaded
3. **Is database empty?** Look for "Total records loaded: 97563"
4. **Port conflict?** `netstat -ano | findstr 8001`
5. **JSON corrupted?** Verify file: `python -m json.tool backend/train_data.json | head`
