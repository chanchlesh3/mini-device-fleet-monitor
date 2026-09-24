from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class DeviceCreate(BaseModel):
    id: str = Field(..., description="Unique identifier for the device")
    name: str = Field(..., description="Human-readable name for the device")

class HeartbeatCreate(BaseModel):
    timestamp: datetime = Field(..., description="ISO8601 timestamp of the heartbeat")
    status: str = Field("OK", description="Status string reported by device")
    cpu_usage: Optional[float] = Field(None, description="Optional CPU usage metric")
    signal_strength: Optional[int] = Field(None, description="Optional signal strength metric")

class DeviceResponse(BaseModel):
    id: str
    name: str
    status: str  # Computed: "ONLINE" or "OFFLINE"
    last_heartbeat: Optional[datetime] = None
    cpu_usage: Optional[float] = None
    signal_strength: Optional[int] = None

class FleetSummaryResponse(BaseModel):
    total: int
    online: int
    offline: int