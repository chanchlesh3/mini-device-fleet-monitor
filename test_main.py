from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
from main import app, devices_db

client = TestClient(app)

def setup_function():
    devices_db.clear()

def test_register_device():
    response = client.post("/devices", json={"id": "test-dev-1", "name": "Test Device"})
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == "test-dev-1"
    assert data["status"] == "OFFLINE"

def test_duplicate_registration():
    client.post("/devices", json={"id": "test-dev-1", "name": "Test Device"})
    response = client.post("/devices", json={"id": "test-dev-1", "name": "Test Device Duplicate"})
    assert response.status_code == 400

def test_heartbeat_and_online_status():
    client.post("/devices", json={"id": "test-dev-1", "name": "Test Device"})
    
    # Send recent heartbeat
    now_iso = datetime.now(timezone.utc).isoformat()
    hb_response = client.post("/devices/test-dev-1/heartbeat", json={"timestamp": now_iso, "status": "OK"})
    assert hb_response.status_code == 200
    
    # Check device status
    res = client.get("/devices/test-dev-1")
    assert res.status_code == 200
    assert res.json()["status"] == "ONLINE"
    
    # Check summary
    summary = client.get("/summary").json()
    assert summary["total"] == 1
    assert summary["online"] == 1
    assert summary["offline"] == 0

def test_offline_timeout_status():
    client.post("/devices", json={"id": "test-dev-1", "name": "Test Device"})
    
    # Send old heartbeat (> 30 seconds ago)
    old_time = datetime.now(timezone.utc) - timedelta(seconds=45)
    client.post("/devices/test-dev-1/heartbeat", json={"timestamp": old_time.isoformat(), "status": "OK"})
    
    # Status should resolve to OFFLINE due to timeout rule
    res = client.get("/devices/test-dev-1")
    assert res.json()["status"] == "OFFLINE"
    
    summary = client.get("/summary").json()
    assert summary["online"] == 0
    assert summary["offline"] == 1