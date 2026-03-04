#!/usr/bin/env python3
"""
API Testing Script for Indian Railways Health Index Backend
Run this to verify all endpoints are working
"""
import requests
import json
from time import sleep

BASE_URL = "http://localhost:8001"

def test_api():
    """Test all backend endpoints"""
    
    print("\n" + "="*70)
    print("TESTING INDIAN RAILWAYS HEALTH INDEX BACKEND API")
    print("="*70 + "\n")
    
    # Test 1: Root endpoint
    print("1️⃣  Testing GET / ...")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"   ✅ Status: {response.status_code}")
        print(f"   📄 Response: {json.dumps(response.json(), indent=2)}\n")
    except Exception as e:
        print(f"   ❌ Error: {e}\n")
    
    # Test 2: Health check
    print("2️⃣  Testing GET /health ...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"   ✅ Status: {response.status_code}")
        data = response.json()
        print(f"   📄 Status: {data.get('status')}")
        print(f"   📄 Trains in DB: {data.get('trains_in_database')}\n")
    except Exception as e:
        print(f"   ❌ Error: {e}\n")
    
    # Test 3: List trains
    print("3️⃣  Testing GET /list-trains ...")
    try:
        response = requests.get(f"{BASE_URL}/list-trains?skip=0&limit=3")
        print(f"   ✅ Status: {response.status_code}")
        data = response.json()
        print(f"   📄 Total trains: {data.get('total')}")
        print(f"   📄 Returned: {len(data.get('trains', []))} trains")
        if data.get('trains'):
            print(f"   📄 Sample train: {data['trains'][0]['train_name']}\n")
        else:
            print(f"   ❌ No trains returned!\n")
    except Exception as e:
        print(f"   ❌ Error: {e}\n")
    
    # Test 4: Get specific train
    print("4️⃣  Testing GET /get-train/10103 ...")
    try:
        response = requests.get(f"{BASE_URL}/get-train/10103")
        print(f"   ✅ Status: {response.status_code}")
        data = response.json()
        print(f"   📄 Train: {data.get('train_name')}")
        print(f"   📄 Route: {data.get('source_station_name')} → {data.get('destination_station_name')}")
        print(f"   📄 Distance: {data.get('distance')} km\n")
    except Exception as e:
        print(f"   ❌ Error: {e}\n")
    
    # Test 5: Generate THI
    print("5️⃣  Testing POST /generate-thi ...")
    try:
        response = requests.post(f"{BASE_URL}/generate-thi?train_no=10103")
        print(f"   ✅ Status: {response.status_code}")
        data = response.json()
        print(f"   📊 THI Score: {data.get('thi_score')}/100")
        print(f"   ⏰ Timestamp: {data.get('timestamp')}")
        print(f"   💬 Suggestion: {data.get('maintenance_suggestion')}")
        print(f"   🔍 Sensor Data:")
        for sensor, value in data.get('sensor_data', {}).items():
            print(f"      - {sensor}: {value}")
        print()
    except Exception as e:
        print(f"   ❌ Error: {e}\n")
    
    # Test 6: API info
    print("6️⃣  Testing GET /api/info ...")
    try:
        response = requests.get(f"{BASE_URL}/api/info")
        print(f"   ✅ Status: {response.status_code}")
        data = response.json()
        print(f"   📄 API Name: {data.get('api_name')}")
        print(f"   📄 Version: {data.get('version')}")
        print(f"   📄 Endpoints available: {len(data.get('endpoints', {}))}\n")
    except Exception as e:
        print(f"   ❌ Error: {e}\n")
    
    print("="*70)
    print("TEST SUMMARY")
    print("="*70)
    print("✅ If all tests passed, your backend is working correctly!")
    print("📍 Frontend: http://localhost:8000")
    print("📍 Backend: http://localhost:8001")
    print("📍 Dagster: http://localhost:3000")
    print("="*70 + "\n")

if __name__ == "__main__":
    print("Waiting for API to be ready...\n")
    sleep(2)
    test_api()
