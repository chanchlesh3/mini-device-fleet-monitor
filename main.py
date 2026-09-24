from datetime import datetime, timezone
from typing import Dict, List
import threading
from fastapi import FastAPI, HTTPException, status
from models import DeviceCreate, HeartbeatCreate, DeviceResponse, FleetSummaryResponse

app = FastAPI(title="Mini Device Fleet Monitor", version="1.0.0")

# In-memory database & thread lock
devices_db: Dict[str, dict] = {}
db_lock = threading.Lock()

TIMEOUT_SECONDS = 30

def compute_status(last_heartbeat: datetime | None) -> str:
    if not last_heartbeat:
        return "OFFLINE"
    
    # Ensure timezone-aware comparison
    now = datetime.now(timezone.utc)
    if last_heartbeat.tzinfo is None:
        last_heartbeat = last_heartbeat.replace(tzinfo=timezone.utc)
        
    delta = (now - last_heartbeat).total_seconds()
    return "ONLINE" if delta <= TIMEOUT_SECONDS else "OFFLINE"

@app.post("/devices", response_model=DeviceResponse, status_code=status.HTTP_201_CREATED)
def register_device(device: DeviceCreate):
    with db_lock:
        if device.id in devices_db:
            raise HTTPException(status_code=400, detail="Device already registered")
        
        devices_db[device.id] = {
            "id": device.id,
            "name": device.name,
            "last_heartbeat": None,
            "cpu_usage": None,
            "signal_strength": None
        }
        
        return DeviceResponse(
            id=device.id,
            name=device.name,
            status="OFFLINE",
            last_heartbeat=None
        )

@app.post("/devices/{device_id}/heartbeat", status_code=status.HTTP_200_OK)
def receive_heartbeat(device_id: str, heartbeat: HeartbeatCreate):
    with db_lock:
        if device_id not in devices_db:
            raise HTTPException(status_code=404, detail="Device not found")
        
        device = devices_db[device_id]
        device["last_heartbeat"] = heartbeat.timestamp
        device["cpu_usage"] = heartbeat.cpu_usage
        device["signal_strength"] = heartbeat.signal_strength
        
        return {"message": "Heartbeat received successfully", "device_id": device_id}

@app.get("/devices", response_model=List[DeviceResponse])
def list_devices():
    with db_lock:
        result = []
        for dev in devices_db.values():
            current_status = compute_status(dev["last_heartbeat"])
            result.append(DeviceResponse(
                id=dev["id"],
                name=dev["name"],
                status=current_status,
                last_heartbeat=dev["last_heartbeat"],
                cpu_usage=dev["cpu_usage"],
                signal_strength=dev["signal_strength"]
            ))
        return result

@app.get("/devices/{device_id}", response_model=DeviceResponse)
def get_device(device_id: str):
    with db_lock:
        if device_id not in devices_db:
            raise HTTPException(status_code=404, detail="Device not found")
        
        dev = devices_db[device_id]
        current_status = compute_status(dev["last_heartbeat"])
        return DeviceResponse(
            id=dev["id"],
            name=dev["name"],
            status=current_status,
            last_heartbeat=dev["last_heartbeat"],
            cpu_usage=dev["cpu_usage"],
            signal_strength=dev["signal_strength"]
        )

@app.get("/summary", response_model=FleetSummaryResponse)
def get_fleet_summary():
    with db_lock:
        total = len(devices_db)
        online = 0
        offline = 0
        
        for dev in devices_db.values():
            if compute_status(dev["last_heartbeat"]) == "ONLINE":
                online += 1
            else:
                offline += 1
                
        return FleetSummaryResponse(total=total, online=online, offline=offline)