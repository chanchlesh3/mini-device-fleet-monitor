import time
import requests
from datetime import datetime, timezone

BASE_URL = "http://127.0.0.1:8000"

DEVICES = [
    {"id": "device-01", "name": "Lab Sensor Alpha"},
    {"id": "device-02", "name": "Lab Sensor Beta"},
    {"id": "device-03", "name": "Factory Monitor Gamma"},
    {"id": "device-04", "name": "Warehouse Delta"},
    {"id": "device-05", "name": "Server Room Epsilon"}
]

def register_devices():
    for dev in DEVICES:
        try:
            res = requests.post(f"{BASE_URL}/devices", json=dev)
            if res.status_code == 201:
                print(f"Registered: {dev['id']}")
            elif res.status_code == 400:
                print(f"Device already exists: {dev['id']}")
            else:
                print(f"Failed to register {dev['id']}: {res.text}")
        except Exception as e:
            print(f"Error connecting to server while registering {dev['id']}: {e}")

def run_simulation():
    print("Starting device simulator. Press Ctrl+C to stop.")
    register_devices()
    
    try:
        while True:
            for dev in DEVICES:
                payload = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "status": "OK",
                    "cpu_usage": 42.5,
                    "signal_strength": -65
                }
                try:
                    res = requests.post(f"{BASE_URL}/devices/{dev['id']}/heartbeat", json=payload)
                    if res.status_code == 200:
                        print(f"Heartbeat sent for {dev['id']}")
                    else:
                        print(f"Failed heartbeat for {dev['id']}: {res.status_code}")
                except Exception as e:
                    print(f"Connection error for {dev['id']}: {e}")
            
            print("-" * 40)
            time.sleep(5)
    except KeyboardInterrupt:
        print("\nSimulator stopped by user.")

if __name__ == "__main__":
    run_simulation()