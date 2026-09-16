import time
import requests
import random
import uuid

API_URL = "http://localhost:8000/api/v1/iot/telemetry"

def simulate_stream():
    print("Starting IoT Telemetry Simulation...")
    # Using a deterministic hardcoded UUID for demo mine (or fetch it)
    # Let's get the first mine ID from the database using a dummy auth or assume it's created.
    # We will just generate realistic fluctuations.
    
    # In a real demo, we need a valid mine_id. We can get it via /api/v1/hierarchy/mines if we login,
    # but since it's a script, let's login first.
    
    login_url = "http://localhost:8000/api/v1/auth/login"
    login_data = {"username": "admin@coalmine.gov.in", "password": "admin123"}
    try:
        r = requests.post(login_url, data=login_data)
        token = r.json().get("access_token")
    except Exception as e:
        print("Backend not running or login failed. Make sure to run `run_seed.ps1` first.")
        return

    headers = {"Authorization": f"Bearer {token}"}
    
    # Get Mine ID
    r = requests.get("http://localhost:8000/api/v1/hierarchy/mines", headers=headers)
    mines = r.json()
    if not mines:
        print("No mines found!")
        return
    mine_id = mines[0]["id"]
    
    base_methane = 0.2
    
    try:
        while True:
            # Simulate a gradual spike
            base_methane += random.uniform(-0.02, 0.1)
            
            payload = {
                "mine_id": mine_id,
                "parameter": "Methane",
                "value": round(base_methane, 2),
                "unit": "%",
                "location_id": "SENSOR-L1-VENT-3"
            }
            print(f"Sending telemetry: {payload}")
            r = requests.post(API_URL, json=payload, headers=headers)
            print(f"Response: {r.status_code}")
            
            if base_methane > 1.2:
                print("\nCRITICAL ALERT TRIGGERED IN BACKEND!")
                break
                
            time.sleep(2)
    except KeyboardInterrupt:
        print("Simulation stopped.")

if __name__ == "__main__":
    simulate_stream()
