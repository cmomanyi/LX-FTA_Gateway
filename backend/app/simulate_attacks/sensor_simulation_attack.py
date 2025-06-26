from fastapi import APIRouter, Request, HTTPException, Body
from fastapi.responses import JSONResponse
from typing import List, Dict
from datetime import datetime, timedelta
from collections import defaultdict
import asyncio
import hashlib
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import boto3

from app.simulate_attacks.attack_log import log_attack, get_attack_logs
from app.simulate_attacks.attack_request import AttackRequest
from app.simulate_attacks.FirmwareUpload import FirmwareUpload
from app.simulate_attacks.ml_evasion_detector import SensorReading, model
from app.simulate_attacks.spoofing_threat import SpoofingRequest
from app.simulate_attacks.replay_threat import ReplayRequest, is_fresh_timestamp, USED_NONCES

router = APIRouter()
dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
executor = ThreadPoolExecutor()

# Used to simulate rate-limiting per sensor for DDoS
_ddos_window: Dict[str, List[datetime]] = defaultdict(list)
_alerts_cache = []


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


async def validate_sensor_id(sensor_id: str):
    valid_ids = await fetch_all_sensor_ids()
    if sensor_id not in valid_ids:
        raise HTTPException(status_code=400, detail="Invalid sensor ID")
    return True


@router.get("/api/sensor-types")
async def get_sensor_types():
    sensor_ids = await fetch_all_sensor_ids()
    return {
        "sensor_types": ["soil", "water", "plant", "atmospheric", "threat"],
        "sensor_ids": sensor_ids
    }


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
            },
            {"type": "sensor_hijack", "description": "Simulates a hijacked sensor stream", "sample": {"sensor_id": "sensor-x"}},
            {"type": "api_abuse", "description": "Simulates abuse of open API endpoints", "sample": {"sensor_id": "sensor-x"}},
            {"type": "tamper_breach", "description": "Simulates unauthorized tampering", "sample": {"sensor_id": "sensor-x"}},
            {"type": "side_channel", "description": "Simulates side-channel data leakage", "sample": {"sensor_id": "sensor-x"}}
        ]
    }


@router.post("/simulate/spoofing")
async def simulate_spoofing_attack(data: SpoofingRequest = Body(...)):
    await validate_sensor_id(data.sensor_id)
    expected_sig = hashlib.sha256((data.sensor_id + data.payload).encode()).hexdigest()
    is_invalid = data.ecc_signature != expected_sig

    message = "🔴 Spoofing attack simulated — ECC Signature Mismatch" if is_invalid else "✅ Signature appears valid"
    severity = "High" if is_invalid else "None"
    blocked = is_invalid

    log_attack(data.sensor_id, "spoofing", message, severity=severity)
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "sensor_id": data.sensor_id,
        "attack_type": "spoofing",
        "message": message,
        "severity": severity,
        "blocked": blocked
    }


@router.post("/simulate/replay")
async def simulate_replay_attack(req: ReplayRequest):
    await validate_sensor_id(req.sensor_id)
    if req.nonce in USED_NONCES:
        message = "🔴 Replay Detected — Duplicate Nonce"
        severity = "High"
        blocked = True
    elif not is_fresh_timestamp(req.timestamp):
        raise HTTPException(status_code=400, detail="Stale timestamp")
    else:
        USED_NONCES.add(req.nonce)
        message = "✅ Payload Accepted — Fresh Nonce"
        severity = "None"
        blocked = False

    log_attack(req.sensor_id, "replay", message, severity=severity)
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "sensor_id": req.sensor_id,
        "attack_type": "replay",
        "message": message,
        "severity": severity,
        "blocked": blocked
    }


@router.post("/simulate/firmware")
async def simulate_firmware_attack(data: FirmwareUpload):
    await validate_sensor_id(data.sensor_id)
    is_valid_signature = data.firmware_signature == "valid_signature_123"
    message = "🔴 Firmware Rejected — Invalid Signature" if not is_valid_signature else "✅ Firmware Verified"
    severity = "High" if not is_valid_signature else "None"
    blocked = not is_valid_signature

    log_attack(data.sensor_id, "firmware_injection", message, severity=severity)
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "sensor_id": data.sensor_id,
        "attack_type": "firmware_injection",
        "message": message,
        "severity": severity,
        "blocked": blocked
    }


@router.post("/simulate/ml_evasion")
async def simulate_ml_evasion_attack(data: SensorReading):
    await validate_sensor_id(data.sensor_id)
    readings = np.array(data.values).reshape(-1, 1)
    preds = model.predict(readings)
    is_drift = -1 in preds
    message = "🔴 ML Evasion Attempt — Drift Detected" if is_drift else "✅ Sensor Stable — No Drift"
    severity = "High" if is_drift else "None"
    blocked = is_drift

    log_attack(data.sensor_id, "ml_evasion", message, severity=severity)
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "sensor_id": data.sensor_id,
        "attack_type": "ml_evasion",
        "message": message,
        "severity": severity,
        "blocked": blocked
    }


@router.post("/simulate/ddos")
async def simulate_ddos_attack(request: Request):
    data = await request.json()
    sensor_id = data.get("sensor_id")
    threshold = data.get("threshold", 10)
    await validate_sensor_id(sensor_id)

    now = datetime.utcnow()
    _ddos_window[sensor_id].append(now)
    _ddos_window[sensor_id] = [t for t in _ddos_window[sensor_id] if (now - t).total_seconds() <= 10]
    request_count = len(_ddos_window[sensor_id])

    if request_count > threshold:
        message = f"DDoS attack detected — {request_count} requests (threshold: {threshold})"
        severity = "High"
        blocked = True
    else:
        message = f"No DDoS detected — {request_count}/{threshold}"
        severity = "None"
        blocked = False

    log_attack(sensor_id, "ddos", message, severity=severity)
    return {
        "timestamp": now.isoformat(),
        "sensor_id": sensor_id,
        "attack_type": "ddos",
        "message": message,
        "severity": severity,
        "blocked": blocked
    }
@router.post("/simulate/sensor_hijack")
async def simulate_sensor_hijack(data: AttackRequest):
    await validate_sensor_id(data.sensor_id)
    message = "🔴 Sensor Hijack Attempt — Stream Manipulated"
    severity = "High"
    blocked = True
    log_attack(data.sensor_id, "sensor_hijack", message, severity=severity)
    return {"timestamp": datetime.utcnow().isoformat(), "sensor_id": data.sensor_id, "attack_type": "sensor_hijack", "message": message, "severity": severity, "blocked": blocked}


@router.post("/simulate/api_abuse")
async def simulate_api_abuse(data: AttackRequest):
    await validate_sensor_id(data.sensor_id)
    message = "🔴 API Abuse Detected — Unauthorized Access Pattern"
    severity = "High"
    blocked = True
    log_attack(data.sensor_id, "api_abuse", message, severity=severity)
    return {"timestamp": datetime.utcnow().isoformat(), "sensor_id": data.sensor_id, "attack_type": "api_abuse", "message": message, "severity": severity, "blocked": blocked}


@router.post("/simulate/tamper_breach")
async def simulate_tamper_breach(data: AttackRequest):
    await validate_sensor_id(data.sensor_id)
    message = "🔴 Tamper Breach — Physical Layer Compromised"
    severity = "High"
    blocked = True
    log_attack(data.sensor_id, "tamper_breach", message, severity=severity)
    return {"timestamp": datetime.utcnow().isoformat(), "sensor_id": data.sensor_id, "attack_type": "tamper_breach", "message": message, "severity": severity, "blocked": blocked}


@router.post("/simulate/side_channel")
async def simulate_side_channel(data: AttackRequest):
    await validate_sensor_id(data.sensor_id)
    message = "🔴 Side-Channel Leak — Timing/Data Access Exploited"
    severity = "High"
    blocked = True
    log_attack(data.sensor_id, "side_channel", message, severity=severity)
    return {"timestamp": datetime.utcnow().isoformat(), "sensor_id": data.sensor_id, "attack_type": "side_channel", "message": message, "severity": severity, "blocked": blocked}



@router.get("/api/logs")
def fetch_logs():
    return {"logs": get_attack_logs()}


@router.get("/api/alerts")
def get_latest_alerts():
    if not _alerts_cache:
        for _ in range(3):
            _alerts_cache.append({
                "timestamp": datetime.utcnow().isoformat(),
                "sensor_id": "sensor-x",
                "message": "Simulated live alert",
                "level": "info"
            })
    return JSONResponse(content={"alerts": _alerts_cache[-10:]})
