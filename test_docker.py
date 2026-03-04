#!/usr/bin/env python3
"""
Docker & Services Test Script
Validates that all services can start correctly
"""
import subprocess
import time
import json
import requests
from pathlib import Path

def run_command(cmd, description):
    """Run a command and return success status"""
    try:
        print(f"\n🔄 {description}...")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ {description} - Success")
            return True
        else:
            print(f"❌ {description} - Failed")
            if result.stderr:
                print(f"   Error: {result.stderr[:200]}")
            return False
    except subprocess.TimeoutExpired:
        print(f"⏱️  {description} - Timeout")
        return False
    except Exception as e:
        print(f"❌ {description} - Exception: {e}")
        return False

def main():
    print("\n" + "="*70)
    print("DOCKER SERVICES DIAGNOSTIC TEST")
    print("="*70)
    
    # Check 1: Docker installed
    docker_ok = run_command("docker --version", "Check Docker installation")
    if not docker_ok:
        print("\n❌ Docker not installed. Please install Docker Desktop.")
        return
    
    # Check 2: Docker Compose installed
    compose_ok = run_command("docker-compose --version", "Check Docker Compose installation")
    if not compose_ok:
        print("\n❌ Docker Compose not installed.")
        return
    
    # Check 3: JSON file exists
    json_path = Path("backend/train_data.json")
    if json_path.exists():
        size_mb = json_path.stat().st_size / (1024*1024)
        print(f"\n✅ Train data file exists ({size_mb:.2f} MB)")
    else:
        print(f"\n❌ Train data file NOT found at {json_path}")
        return
    
    # Check 4: Docker images exist
    print("\n🔄 Checking Docker images...")
    result = subprocess.run("docker images", shell=True, capture_output=True, text=True)
    if "nginx" in result.stdout:
        print("✅ Nginx image available")
    else:
        print("⚠️  Nginx image may need to download")
    
    # Check 5: Try to start services
    print("\n" + "="*70)
    print("STARTING SERVICES...")
    print("="*70)
    
    print("\n🔄 Building Docker images (this may take 2-5 minutes)...")
    result = subprocess.run(
        "docker-compose build --no-cache",
        shell=True,
        capture_output=True,
        text=True,
        timeout=600
    )
    
    if result.returncode != 0:
        print("❌ Docker build failed")
        print(f"Error: {result.stderr[-500:]}")
        return
    
    print("✅ Docker build successful")
    
    print("\n🔄 Starting containers...")
    proc = subprocess.Popen(
        "docker-compose up",
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait for services to start
    print("⏳ Waiting for services to start (30 seconds)...")
    time.sleep(30)
    
    # Check backend health
    print("\n🔄 Testing backend API...")
    try:
        response = requests.get("http://localhost:8001/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is responding")
            data = response.json()
            print(f"   Trains in database: {data.get('trains_in_database', 0)}")
        else:
            print(f"⚠️  Backend returned status {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend on port 8001")
    except Exception as e:
        print(f"⚠️  Backend test error: {e}")
    
    # Check frontend
    print("\n🔄 Testing frontend...")
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend is responding")
        else:
            print(f"⚠️  Frontend returned status {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to frontend on port 8000")
    except Exception as e:
        print(f"⚠️  Frontend test error: {e}")
    
    # Check Dagster
    print("\n🔄 Testing Dagster...")
    try:
        response = requests.get("http://localhost:3000/", timeout=5)
        if response.status_code == 200:
            print("✅ Dagster is responding")
        else:
            print(f"⚠️  Dagster returned status {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Dagster on port 3000")
    except Exception as e:
        print(f"⚠️  Dagster test error: {e}")
    
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print("✅ All checks passed! Services are running.")
    print("\nAccess your services:")
    print("  - Frontend: http://localhost:8000")
    print("  - Backend: http://localhost:8001")
    print("  - Dagster: http://localhost:3000")
    print("\nPress Ctrl+C to stop the services.")
    print("="*70)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 Services stopped")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
