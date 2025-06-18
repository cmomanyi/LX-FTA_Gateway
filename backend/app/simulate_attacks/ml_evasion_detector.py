import numpy as np
from sklearn.ensemble import IsolationForest
from pydantic import BaseModel
from typing import List
from datetime import datetime
# ----------------------
# Simulated Training Data (Normal Sensor Behavior)
# ----------------------
normal_sensor_data = np.array([
    [22.0], [22.5], [21.8], [22.1], [21.9],
    [22.2], [22.4], [21.7], [22.0], [22.3]
])

# Train Isolation Forest on normal data
model = IsolationForest(contamination=0.1, random_state=42)
model.fit(normal_sensor_data)

# ----------------------
# Input schema
# ----------------------
class SensorReading(BaseModel):
    sensor_id: str
    values: List[float]  # recent time-series sensor values