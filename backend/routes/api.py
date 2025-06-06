from fastapi import APIRouter, WebSocket
from backend.models.models import SensorData
from detector.detector import detect_spoofing, detect_replay
from database.database import anomaly_logs
from typing import List

router = APIRouter()


@router.post("/sensor/threat")
def simulate_sensor(data: SensorData):
    log1 = detect_spoofing(data)
    if log1:
        anomaly_logs.append(log1)
        return log1
    log2 = detect_replay(data)
    if log2:
        anomaly_logs.append(log2)
        return log2
    return {"message": "No anomaly detected"}


@router.get("/anomalies", response_model=List[dict])
def get_anomalies():
    return [log.dict() for log in anomaly_logs]


@router.websocket("/ws/alerts")
async def alert_websocket(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            for log in anomaly_logs[-5:]:
                await websocket.send_json(log.dict())
    except Exception:
        await websocket.close()
