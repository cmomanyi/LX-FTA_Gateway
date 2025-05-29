from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, Any
import asyncio
import json

router = APIRouter()

# Store request times and logs
sensor_request_log: Dict[str, list] = defaultdict(list)
audit_trail = []
clients = set()

# DDoS detection configuration
WINDOW_SECONDS = 10
MAX_REQUESTS_PER_WINDOW = 5


@router.post("/sensor/threat/{threat_type}")
async def detect_threat(threat_type: str, request: Request):
    data = await request.json()
    sensor_id = data.get("sensor_id")
    message = data.get("message", "")
    timestamp = datetime.utcnow()

    # Track requests for DDoS
    sensor_request_log[sensor_id].append(timestamp)
    sensor_request_log[sensor_id] = [
        t for t in sensor_request_log[sensor_id]
        if t > timestamp - timedelta(seconds=WINDOW_SECONDS)
    ]
    request_count = len(sensor_request_log[sensor_id])
    is_ddos = threat_type == "ddos" and request_count > MAX_REQUESTS_PER_WINDOW

    result = {
        "timestamp": timestamp.isoformat(),
        "sensor_id": sensor_id,
        "attack_type": "ddos" if is_ddos else threat_type,
        "message": "DDoS detected: Too many requests" if is_ddos else message,
        "severity": "High" if is_ddos else data.get("severity", "Medium"),
        "status": "blocked" if is_ddos else "accepted"
    }

    audit_trail.append(result)
    return result


@router.websocket("/ws/alerts")
async def alerts_ws(websocket: WebSocket):
    await websocket.accept()
    clients.add(websocket)
    try:
        while True:
            if audit_trail:
                await websocket.send_json(audit_trail[-1])
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        clients.remove(websocket)


@router.get("/audit/logs")
def get_audit_log():
    return JSONResponse(content=audit_trail)


def save_audit_log_to_disk(path="audit_log.json"):
    with open(path, "w") as f:
        json.dump(audit_trail, f, indent=2)
