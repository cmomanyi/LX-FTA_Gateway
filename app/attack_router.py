from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, Response
from attacks.attack_detector import (
    detect_spoofing, detect_replay, detect_firmware_tampering,
    detect_ml_evasion, detect_overflow, detect_ddos,
    detect_api_abuse, detect_side_channel, detect_tamper_breach,
    detect_sensor_hijack
)
import json
import os

router = APIRouter()

clients = set()


@router.get("/api/audit")
async def get_audit():
    if os.path.exists("security_events_log.json"):
        with open("security_events_log.json", "r") as f:
            logs = [json.loads(line.strip()) for line in f.readlines()]
        return JSONResponse(content=logs[::-1])  # newest first
    return []


@router.websocket("/ws/alerts")
async def alerts(websocket: WebSocket):
    await websocket.accept()
    clients.add(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        clients.remove(websocket)


# Broadcast utility
async def broadcast_alert(event):
    for client in clients:
        try:
            await client.send_text(json.dumps(event))
        except:
            pass


# Injected into detector
def log_attack(attack_type, message, severity="High", sensor_id=None, target="unspecified"):
    from datetime import datetime
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "attack_type": attack_type,
        "message": message,
        "status": "Blocked",
        "severity": severity,
        "target": target,
    }
    if sensor_id:
        entry["sensor_id"] = sensor_id
        entry["sensor"] = sensor_id
    with open("security_events_log.json", "a") as f:
        f.write(json.dumps(entry) + "\n")
    try:
        import asyncio
        asyncio.create_task(broadcast_alert(entry))
    except:
        pass
    return entry


@router.get("/trigger")
async def trigger_from_dashboard(attack: str = "spoofing"):
    from datetime import datetime
    import os
    nonce = os.urandom(8)
    if attack == "spoofing":
        detect_spoofing(False, "soil_01")
    elif attack == "replay":
        detect_replay(datetime.utcnow(), nonce, "soil_01")
    elif attack == "firmware":
        detect_firmware_tampering("tampered_hash", "soil_01")
    elif attack == "ml":
        detect_ml_evasion(0.1, "soil_01")
    elif attack == "overflow":
        detect_overflow("X" * 2001, "soil_01")
    elif attack == "ddos":
        detect_ddos("soil_01")
    elif attack == "api":
        detect_api_abuse("viewer", "/firmware-update", "soil_01")
    elif attack == "sidechannel":
        detect_side_channel(0.95, 0.95, "soil_01")
    elif attack == "tamper":
        detect_tamper_breach("tampered_config", "soil_01")
    elif attack == "hijack":
        detect_sensor_hijack("unauth_sensor_05")
    else:
        return {"status": f"Unknown attack type: {attack}"}
    return {"status": f"Triggered {attack} attack"}
