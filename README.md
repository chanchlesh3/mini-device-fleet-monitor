# Mini Device Fleet Monitor

A lightweight backend application built to monitor a fleet of simulated devices, track their heartbeats, and dynamically evaluate their operational status (**ONLINE** or **OFFLINE**).

---

## 1. What the Project Does
The **Mini Device Fleet Monitor** provides a REST API backend that:
- Registers new devices.
- Receives periodic heartbeats from registered devices.
- Automatically calculates whether a device is **ONLINE** or **OFFLINE** based on a **30-second timeout rule**.
- Provides summary metrics and detailed status views for the entire fleet.
- Includes an automated test suite and a live device simulator script.

---

## 2. Design / Architecture
- **Framework:** **FastAPI** (Python) chosen for high performance, automatic data validation via Pydantic, and built-in interactive Swagger documentation.
- **State Management:** Thread-safe in-memory dictionary utilizing `threading.Lock` to handle concurrent heartbeat updates and API reads safely.
- **Dynamic Status Evaluation:** Status (`ONLINE`/`OFFLINE`) is computed on-the-fly during read requests by comparing the current UTC timestamp against `last_heartbeat + 30 seconds`, avoiding complex background polling workers.

---

## 3. Prerequisites
- Python 3.10 or higher installed on your system.

---

## 4. How to Build / Setup Application
1. Clone the repository and navigate to the project directory:

    cd mini-device-fleet-monitor

2. Create and activate a virtual environment:

    python -m venv venv
    # On Windows:
    .\venv\Scripts\Activate
    # On macOS/Linux:
    # source venv/bin/activate

3. Install dependencies:

    python -m pip install -r requirements.txt

---

## 5. How to Run the Application
Start the FastAPI backend server using Uvicorn:

    uvicorn main:app --reload

The server will start running at http://127.0.0.1:8000. You can access the interactive API docs at http://127.0.0.1:8000/docs.

---

## 6. How to Run the Simulator
With the server running in one terminal window, open a **second terminal window**, activate your virtual environment, and run the simulator script:

    python simulator/simulate.py

This script will register 5 simulated devices and push heartbeats every 5 seconds. You can press Ctrl+C to stop it and watch them transition to **OFFLINE** after 30 seconds.

---

## 7. How to Run the Tests
Run the automated pytest suite to verify core logic and timeout behaviors:

    python -m pytest -v

---

## 8. Example API Requests

### Register a Device (POST /devices)
    curl -X 'POST' \
      'http://127.0.0.1:8000/devices' \
      -H 'accept: application/json' \
      -H 'Content-Type: application/json' \
      -d '{
      "id": "device-01",
      "name": "Lab Device 01"
    }'

### Send Heartbeat (POST /devices/{id}/heartbeat)
    curl -X 'POST' \
      'http://127.0.0.1:8000/devices/device-01/heartbeat' \
      -H 'accept: application/json' \
      -H 'Content-Type: application/json' \
      -d '{
      "timestamp": "2026-09-24T10:30:00Z",
      "status": "OK",
      "cpu_usage": 42.5,
      "signal_strength": -65
    }'

### Get Fleet Summary (GET /summary)
    curl -X 'GET' 'http://127.0.0.1:8000/summary' -H 'accept: application/json'

---

## 9. Assumptions Made
- Device IDs are unique string identifiers provided upon registration.
- Timestamps sent in heartbeats are parsed as ISO8601 UTC datetimes.
- In-memory storage is sufficient for this scope; data does not need to persist across server restarts.

---

## 10. Known Limitations
- Server restarts will clear all registered devices and heartbeat history because storage is kept in-memory.
- Scale is limited by single-server memory capacity.

---

## 11. What You Would Improve If You Had One Additional Day
- Integrate a persistent database (such as PostgreSQL or SQLite) using SQLAlchemy or SQLModel.
- Add a lightweight frontend dashboard (using Streamlit or Tailwind CSS) to visualize the fleet status in real time.
- Implement token-based authentication for secure device registration.

---

## AI Usage
- **AI Tools Used:** Gemini.
- **What it was used for:** Scaffolding the FastAPI application structure, designing thread-safe in-memory state management, writing the device simulator script, and creating pytest test cases.
- **Code Changed/Improved:** Adjusted timezone awareness handling for heartbeat timestamps to ensure precise datetime comparisons against the 30-second window.
- **Personal Verification:** Personally verified the end-to-end workflow by running the Uvicorn server, executing the device simulator, confirming live offline status transitions after terminating the script, and passing all pytest test cases.
