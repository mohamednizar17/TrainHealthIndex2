"""
Indian Railways Health Index - FastAPI Backend
Generates THI scores based on sensor data and provides train information
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json
import random
import os
from datetime import datetime
from pydantic import BaseModel
from pathlib import Path

# ==================== INITIALIZATION ====================
print("\n" + "="*70)
print("STARTING INDIAN RAILWAYS HEALTH INDEX BACKEND")
print("="*70)

app = FastAPI(
    title="Indian Railways Health Index API",
    description="API for accessing train data and generating THI scores",
    version="1.0.0"
)

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== LOAD TRAIN DATA ====================
def load_train_data():
    """Load train data from JSON file"""
    print("\n📂 Searching for train data file...")
    print(f"   Current working directory: {os.getcwd()}")
    print(f"   Script location: {Path(__file__).parent}")
    
    try:
        # Try multiple paths for different environments
        json_paths = [
            Path(__file__).parent / "train_data.json",
            Path("/app/train_data.json"),
            Path(__file__).parent.parent / "TrainHealthIndex" / "train_max_distance_only.json",
            Path.cwd() / "train_data.json",
            Path.cwd() / "TrainHealthIndex" / "train_max_distance_only.json",
        ]
        
        print(f"\n   Checking {len(json_paths)} possible locations:")
        for idx, json_path in enumerate(json_paths, 1):
            exists = json_path.exists()
            status = "✅ EXISTS" if exists else "❌ NOT FOUND"
            print(f"   {idx}. {json_path} [{status}]")
            
            if exists:
                try:
                    print(f"\n   🔄 Loading from: {json_path}")
                    with open(json_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        print(f"   ✅ Successfully loaded {len(data)} train records")
                        
                        # Print sample records
                        if data:
                            print(f"\n   📊 Sample records:")
                            for sample in data[:2]:
                                print(f"      - Train {sample.get('Train No')}: {sample.get('Train Name')}")
                        
                        return data
                except json.JSONDecodeError as je:
                    print(f"   ⚠️ JSON Parse Error: {je}")
                    continue
                except Exception as inner_e:
                    print(f"   ⚠️ Error reading file: {inner_e}")
                    continue
        
        print(f"\n   ❌ Train data file not found in any location!")
        return []
    except Exception as e:
        print(f"   ❌ Error loading train data: {e}")
        import traceback
        traceback.print_exc()
        return []

TRAIN_DATA = load_train_data()

print(f"\n📊 DATA STATUS:")
print(f"   ✅ Total records loaded: {len(TRAIN_DATA)}")
if TRAIN_DATA:
    unique_trains = len(set(t.get("Train No") for t in TRAIN_DATA))
    print(f"   ✅ Unique trains: {unique_trains}")
else:
    print(f"   ⚠️ WARNING: No train data loaded! API will be empty.")

print("\n" + "="*70)
print(f"✅ Backend initialized successfully")
print("="*70 + "\n")

# ==================== DATA MODELS ====================
class SensorData(BaseModel):
    """Sensor data model"""
    brake_temperature: float
    axle_vibration: float
    wheel_wear: float
    engine_load: float
    battery_voltage: float
    fuel_efficiency: float

class THIResponse(BaseModel):
    """THI calculation response"""
    train_no: int
    timestamp: str
    sensor_data: dict
    thi_score: int
    maintenance_suggestion: str

class TrainInfo(BaseModel):
    """Train information response"""
    train_no: int
    train_name: str
    source_station: str
    source_station_name: str
    destination_station: str
    destination_station_name: str
    distance: float

# ==================== SENSOR DATA GENERATION ====================
def generate_sensor_data() -> dict:
    """
    Generate realistic sensor data based on operational parameters
    
    Returns:
        dict: Dictionary containing sensor readings
    """
    return {
        "Brake Temperature (°C)": round(random.uniform(30, 120), 2),
        "Axle Vibration (mm/s)": round(random.uniform(0.1, 4.0), 2),
        "Wheel Wear (%)": round(random.uniform(10, 90), 2),
        "Engine Load (%)": round(random.uniform(40, 100), 2),
        "Battery Voltage (V)": round(random.uniform(10.5, 14.5), 2),
        "Fuel Efficiency (km/L)": round(random.uniform(2, 5), 2)
    }

# ==================== THI CALCULATION ====================
def calculate_thi(sensor_data: dict) -> tuple[int, str]:
    """
    Calculate Train Health Index based on sensor data
    
    Algorithm:
    - Start with 100 points
    - Deduct points based on sensor readings exceeding thresholds
    - Return final score (0-100) and maintenance suggestion
    
    Args:
        sensor_data: Dictionary with sensor readings
        
    Returns:
        tuple: (THI score, maintenance suggestion)
    """
    score = 100
    
    # Brake Temperature check (should be < 90°C)
    if sensor_data.get("Brake Temperature (°C)", 0) > 90:
        score -= 15
    
    # Axle Vibration check (should be < 2.5 mm/s)
    if sensor_data.get("Axle Vibration (mm/s)", 0) > 2.5:
        score -= 20
    
    # Wheel Wear check (should be < 70%)
    if sensor_data.get("Wheel Wear (%)", 0) > 70:
        score -= 25
    
    # Engine Load check (should be < 85%)
    if sensor_data.get("Engine Load (%)", 0) > 85:
        score -= 10
    
    # Battery Voltage check (should be >= 11V)
    if sensor_data.get("Battery Voltage (V)", 0) < 11:
        score -= 10
    
    # Fuel Efficiency check (should be >= 3 km/L)
    if sensor_data.get("Fuel Efficiency (km/L)", 0) < 3:
        score -= 10
    
    # Ensure score is within 0-100 range
    score = max(0, min(100, score))
    
    # Determine maintenance suggestion based on score
    if score >= 80:
        maintenance = "✅ Train in excellent condition. Routine checks sufficient."
    elif score >= 50:
        maintenance = "⚠️ Schedule maintenance within 48 hours."
    else:
        maintenance = "❌ Critical issues detected. Immediate inspection required!"
    
    return score, maintenance

# ==================== STARTUP EVENT ====================

@app.on_event("startup")
async def startup_event():
    """Verify data is loaded when app starts"""
    print("\n" + "="*70)
    print("🚀 BACKEND STARTUP STATUS")
    print("="*70)
    print(f"✅ API Server running on http://0.0.0.0:8001")
    print(f"📊 Train records available: {len(TRAIN_DATA)}")
    
    if TRAIN_DATA:
        unique = len(set(t.get("Train No") for t in TRAIN_DATA))
        print(f"🚂 Unique trains: {unique}")
    else:
        print(f"⚠️  WARNING: No train data loaded!")
    
    print(f"📚 API Documentation: http://localhost:8001/docs")
    print("="*70 + "\n")

# ==================== API ENDPOINTS ====================

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "api": "Indian Railways Health Index",
        "version": "1.0.0",
        "endpoints": {
            "get_train": "/get-train/{train_no}",
            "generate_thi": "/generate-thi",
            "list_all_trains": "/list-trains"
        }
    }

@app.get("/get-train/{train_no}", response_model=TrainInfo)
async def get_train(train_no: int):
    """
    Fetch train information by train number
    
    Args:
        train_no: The train number to lookup
        
    Returns:
        TrainInfo: Train details including route information
    """
    print(f"\n🔍 GET /get-train/{train_no}")
    print(f"   Total records in DB: {len(TRAIN_DATA)}")
    
    if not TRAIN_DATA:
        print(f"   ❌ ERROR: Database is empty!")
        raise HTTPException(
            status_code=500,
            detail="Train database is empty. Check if JSON file loaded correctly."
        )
    
    # Find train in data
    train = next((t for t in TRAIN_DATA if t.get("Train No") == train_no), None)
    
    if not train:
        available_trains = sorted(set(t.get("Train No") for t in TRAIN_DATA))[:5]
        print(f"   ❌ Train {train_no} not found")
        print(f"   Available trains (sample): {available_trains}")
        raise HTTPException(
            status_code=404,
            detail=f"Train {train_no} not found in database. Available: {available_trains}"
        )
    
    print(f"   ✅ Found: {train.get('Train Name')}")
    
    return TrainInfo(
        train_no=train.get("Train No"),
        train_name=train.get("Train Name", "Unknown"),
        source_station=train.get("Source Station", "N/A"),
        source_station_name=train.get("Source Station Name", "Unknown"),
        destination_station=train.get("Destination Station", "N/A"),
        destination_station_name=train.get("Destination Station Name", "Unknown"),
        distance=train.get("Distance", 0)
    )

@app.post("/generate-thi", response_model=THIResponse)
async def generate_thi_endpoint(train_no: int = 10103):
    """
    Generate THI score with sensor data
    
    This endpoint:
    1. Generates realistic sensor data
    2. Calculates THI based on the sensor readings
    3. Returns the score with timestamp and maintenance suggestion
    
    Args:
        train_no: Optional train number (default: 10103)
        
    Returns:
        THIResponse: Contains sensor data, THI score, and suggestions
    """
    # Generate sensor data
    sensor_data = generate_sensor_data()
    
    # Calculate THI
    thi_score, maintenance_suggestion = calculate_thi(sensor_data)
    
    # Get current timestamp
    timestamp = datetime.now().isoformat()
    
    return THIResponse(
        train_no=train_no,
        timestamp=timestamp,
        sensor_data=sensor_data,
        thi_score=thi_score,
        maintenance_suggestion=maintenance_suggestion
    )

@app.get("/list-trains")
async def list_all_trains(skip: int = 0, limit: int = 10):
    """
    List all trains with pagination
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        dict: List of trains and pagination info
    """
    print(f"\n📋 GET /list-trains?skip={skip}&limit={limit}")
    print(f"   Total records in DB: {len(TRAIN_DATA)}")
    
    if not TRAIN_DATA:
        print(f"   ⚠️  WARNING: Database is empty!")
        return {
            "total": 0,
            "skip": skip,
            "limit": limit,
            "trains": [],
            "warning": "Train database is empty. Check if JSON file loaded correctly."
        }
    
    unique_trains = {}
    for train in TRAIN_DATA:
        train_no = train.get("Train No")
        if train_no not in unique_trains:
            unique_trains[train_no] = {
                "train_no": train_no,
                "train_name": train.get("Train Name"),
                "source": f"{train.get('Source Station')} - {train.get('Source Station Name')}",
                "destination": f"{train.get('Destination Station')} - {train.get('Destination Station Name')}",
                "distance": train.get("Distance")
            }
    
    trains_list = list(unique_trains.values())
    total = len(trains_list)
    paginated = trains_list[skip:skip + limit]
    
    print(f"   ✅ Total unique trains: {total}")
    print(f"   ✅ Returning: {len(paginated)} trains")
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "trains": paginated
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "trains_in_database": len(set(t.get("Train No") for t in TRAIN_DATA))
    }

# ==================== APP INFO ====================
@app.get("/api/info")
async def api_info():
    """Get API information and available endpoints"""
    return {
        "api_name": "Indian Railways Health Index API",
        "version": "1.0.0",
        "description": "Production-grade API for train health monitoring",
        "endpoints": {
            "GET /get-train/{train_no}": "Fetch train information by number",
            "POST /generate-thi": "Generate THI score with sensor data",
            "GET /list-trains": "List all trains with pagination",
            "GET /health": "Health check endpoint",
            "GET /api/info": "API information"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
