import boto3
import hashlib
import random
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List
from concurrent.futures import ThreadPoolExecutor
import asyncio

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from app.simulate_attacks.attack_log import log_attack, get_attack_logs
from app.simulate_attacks.attack_request import AttackRequest
from app.simulate_attacks.FirmwareUpload import FirmwareUpload
from app.simulate_attacks.ml_evasion_detector import SensorReading, model
from app.simulate_attacks.replay_threat import ReplayRequest, is_fresh_timestamp, USED_NONCES
from app.simulate_attacks.spoofing_threat import SpoofingRequest

router = APIRouter()
dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
executor = ThreadPoolExecutor()


async def fetch_all_sensor_ids():
    tables = [
        "lx-fta-soil-data",
        "lx-fta-atmospheric-data",
        "lx-fta-water-data",
        "lx-fta-threat-data",
        "lx-fta-plant-data"
    ]
    sensor_ids = set()

    def scan_table(table_name):
        try:
            table = dynamodb.Table(table_name)
            response = table.scan(ProjectionExpression="sensor_id")
            return [item["sensor_id"] for item in response.get("Items", []) if "sensor_id" in item]
        except Exception as e:
            print(f"Failed to fetch from {table_name}: {e}")
            return []

    loop = asyncio.get_running_loop()
    tasks = [loop.run_in_executor(executor, scan_table, table) for table in tables]
    results = await asyncio.gather(*tasks)

    for sensor_list in results:
        sensor_ids.update(sensor_list)

    return list(sensor_ids)


@router.get("/api/sensor-types")
async def get_sensor_types():
    sensor_ids = await fetch_all_sensor_ids()
    return {
        "sensor_types": ["soil", "water", "plant", "atmospheric", "threat"],
        "sensor_ids": sensor_ids
    }


async def validate_sensor_id(sensor_id: str):
    valid_ids = await fetch_all_sensor_ids()
    if sensor_id not in valid_ids:
        raise HTTPException(status_code=400, detail="Invalid sensor ID")
    return True


# ---------------- DDoS ----------------
ddos_window: Dict[str, List[datetime]] = defaultdict(list)


@router.get("/api/attack-types")
def get_attack_types():
    return {
        "attack_types": [
            {
                "type": "spoofing",
                "description": "Simulates ECC signature mismatch",
                "sample": {
                    "sensor_id": "sensor-x",
                    "payload": "abc123",
                    "ecc_signature": "invalid_hash"
                }
            },
            {
                "type": "replay",
                "description": "Sends repeated nonce/timestamp values",
                "sample": {
                    "sensor_id": "sensor-x",
                    "timestamp": datetime.utcnow().isoformat(),
                    "nonce": "nonce-123456"
                }
            },
            {
                "type": "firmware",
                "description": "Attempts to upload invalid firmware signature",
                "sample": {
                    "sensor_id": "sensor-x",
                    "firmware_version": "1.0.3",
                    "firmware_signature": "invalid_signature"
                }
            },
            {
                "type": "ml_evasion",
                "description": "Triggers a drift detection anomaly",
                "sample": {
                    "sensor_id": "sensor-x",
                    "values": [1.2, 2.3, 3.4]
                }
            },
            {
                "type": "ddos",
                "description": "Sends many requests in a short timeframe",
                "sample": {
                    "sensor_id": "sensor-x",
                    "threshold": 10
                }
            }
        ]
    }


@router.post("/sensor/threat/ddos")
async def detect_ddos(request: Request):
    data = await request.json()
    sensor_id = data.get("sensor_id")
    threshold = data.get("threshold", 10)
    await validate_sensor_id(sensor_id)
    now = datetime.utcnow()
    ddos_window[sensor_id].append(now)
    ddos_window[sensor_id] = [t for t in ddos_window[sensor_id] if (now - t).total_seconds() <= 10]
    request_count = len(ddos_window[sensor_id])

    if request_count > threshold:
        message = f"DDoS attack detected — {request_count} requests (threshold: {threshold})"
        log_attack(sensor_id, "ddos", message, severity="High")
        return {
            "timestamp": now.isoformat(),
            "sensor_id": sensor_id,
            "attack_type": "ddos",
            "message": message,
            "severity": "High",
            "blocked": True
        }

    message = f"No DDoS detected — {request_count}/{threshold}"
    log_attack(sensor_id, "ddos", message, severity="None")
    return {
        "status": message,
        "message": message,
        "severity": "None",
        "blocked": False
    }


@router.post("/api/detect/firmware_injection")
async def detect_firmware_injection(data: FirmwareUpload):
    await validate_sensor_id(data.sensor_id)
    if not data.firmware_signature or data.firmware_signature != "valid_signature_123":
        message = "🔴 Firmware Rejected – Signature Invalid"
        alert = {
            "timestamp": datetime.utcnow().isoformat(),
            "sensor_id": data.sensor_id,
            "attack_type": "firmware_injection",
            "message": message,
            "severity": "High",
            "blocked": True
        }
        log_attack(data.sensor_id, "firmware_injection", message, severity="High")
        return alert

    return {
        "status": "✅ Firmware accepted and verified",
        "severity": "None",
        "blocked": False
    }


@router.post("/api/validate")
async def spoofing_protection(req: SpoofingRequest):
    sensor_id = req.sensor_id
    await validate_sensor_id(sensor_id)
    expected = hashlib.sha256((sensor_id + req.payload).encode()).hexdigest()
    if req.ecc_signature != expected:
        message = "🔴 Spoofing Detected – ECC Signature Mismatch"
        log_attack(sensor_id, "spoofing", message, severity="High")
        return {
            "status": message,
            "message": message,
            "severity": "High",
            "blocked": True
        }

    message = "✅ Signature Verified"
    log_attack(sensor_id, "spoofing", message, severity="None")
    return {
        "status": message,
        "message": message,
        "severity": "None",
        "blocked": False
    }


@router.post("/api/replay-protect")
async def replay_protection(req: ReplayRequest):
    sensor_id = req.sensor_id
    await validate_sensor_id(sensor_id)
    if req.nonce in USED_NONCES:
        message = "🔴 Replay Detected – Duplicate Nonce"
        log_attack(sensor_id, "replay", message, severity="High")
        return {
            "status": message,
            "message": message,
            "severity": "High",
            "blocked": True
        }
    if not is_fresh_timestamp(req.timestamp):
        raise HTTPException(status_code=400, detail="Stale timestamp")

    USED_NONCES.add(req.nonce)
    message = "✅ Payload Accepted – Fresh Nonce"
    log_attack(sensor_id, "replay", message, severity="None")
    return {
        "status": message,
        "message": message,
        "severity": "None",
        "blocked": False
    }


@router.post("/api/drift-detect")
async def detect_drift(data: SensorReading):
    sensor_id = data.sensor_id
    await validate_sensor_id(sensor_id)
    readings = np.array(data.values).reshape(-1, 1)
    preds = model.predict(readings)

    if -1 in preds:
        message = "🔴 ML Evasion Attempt – Drift Behavior Detected"
        log_attack(sensor_id, "drift", message, severity="High")
        return {
            "status": message,
            "message": message,
            "severity": "High",
            "blocked": True
        }

    message = "✅ Sensor Stable – No Drift"
    log_attack(sensor_id, "drift", message, severity="None")
    return {
        "status": message,
        "message": message,
        "severity": "None",
        "blocked": False
    }


@router.get("/api/logs")
def fetch_logs():
    return {"logs": get_attack_logs()}


# Simulated alerts
alerts_cache = []

def generate_mock_alert():
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "sensor_id": "sensor-x",
        "message": "Simulated live alert",
        "level": "info"
    }

@router.get("/api/alerts")
def get_latest_alerts():
    if not alerts_cache:
        for _ in range(3):
            alerts_cache.append(generate_mock_alert())
    return JSONResponse(content={"alerts": alerts_cache[-10:]})
