from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SensorData(BaseModel):
    sensor_id: str
    metric: float
    timestamp: datetime
    nonce: Optional[str] = None


class AnomalyLog(BaseModel):
    timestamp: datetime
    sensor_id: str
    attack_type: str
    message: str
    severity: str
    status: str
