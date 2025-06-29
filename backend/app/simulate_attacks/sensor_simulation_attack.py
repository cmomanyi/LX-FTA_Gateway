import os
import uuid

import shap
from fastapi import APIRouter, Request, HTTPException, Body
from fastapi.responses import JSONResponse
from typing import List, Dict
from datetime import datetime, timedelta
from collections import defaultdict
import asyncio
import hashlib
import numpy as np
import logging
from concurrent.futures import ThreadPoolExecutor

from starlette.responses import FileResponse


from app.simulate_attacks.attack_log import log_attack, get_attack_logs
from app.simulate_attacks.attack_request import AttackRequest
from app.simulate_attacks.FirmwareUpload import FirmwareUpload
from app.simulate_attacks.ml_evasion_detector import SensorReading, model
from app.simulate_attacks.spoofing_threat import SpoofingRequest, validate_ecc
from app.simulate_attacks.replay_threat import ReplayRequest, is_fresh_timestamp, USED_NONCES
from app.cache.sensor_cache import sensor_id_cache
from app.utils.dynamodb_helper import put_item, scan_table

router = APIRouter()
executor = ThreadPoolExecutor()
_ddos_window: Dict[str, List[datetime]] = defaultdict(list)
_alerts_cache = []
DDB_LOG_TABLE = "lx-fta-audit-logs"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Fetch all sensor IDs from DynamoDB tables
async def fetch_all_sensor_ids_from_tables():
    table_names = [
        "lx-fta-soil-data",
        "lx-fta-water-data",
        "lx-fta-plant-data",
        "lx-fta-atmospheric-data",
        "lx-fta-threat-data"
    ]
    sensor_ids = set()
    loop = asyncio.get_event_loop()
    tasks = [loop.run_in_executor(executor, scan_table, table) for table in table_names]
    results = await asyncio.gather(*tasks)
    for items in results:
        for item in items:
            if "sensor_id" in item:
                sensor_ids.add(item["sensor_id"])
    return sensor_ids


# Fetch valid sensor IDs only once into cache
async def cache_sensor_ids():
    if not sensor_id_cache:
        valid_ids = await fetch_all_sensor_ids_from_tables()
        sensor_id_cache.update(valid_ids)


async def validate_sensor_id(sensor_id: str):
    await cache_sensor_ids()
    if sensor_id not in sensor_id_cache:
        raise HTTPException(status_code=400, detail="Invalid sensor ID")
    return True


def persist_attack_log(sensor_id: str, attack_type: str, message: str, severity: str):
    log_entry = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat(),
        "sensor_id": sensor_id,
        "attack_type": attack_type,
        "message": message,
        "severity": severity
    }
    put_item(DDB_LOG_TABLE, log_entry)
    log_attack(sensor_id, attack_type, message, severity)


@router.post("/simulate/ddos")
async def simulate_ddos_attack(request: Request):
    try:
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
            severity = "🔴 High"
            blocked = True
        else:
            message = f"No DDoS detected — {request_count}/{threshold}"
            severity = "✅ None"
            blocked = False
        put_item(DDB_LOG_TABLE, {
            "timestamp": now.isoformat(),
            "sensor_id": sensor_id,
            "attack_type": "ddos",
            "message": message,
            "severity": severity
        })
        log_attack(sensor_id, "ddos", message, severity)
        return {"timestamp": now.isoformat(), "sensor_id": sensor_id, "attack_type": "ddos", "message": message,
                "severity": severity, "blocked": blocked}
    except Exception as e:
        logger.exception("DDoS simulation failed")
        raise HTTPException(status_code=500, detail=f"Failed to simulate DDoS attack {e}")


@router.post("/simulate/spoofing")
async def simulate_spoofing_attack(data: SpoofingRequest):
    await validate_sensor_id(data.sensor_id)
    # expected_sig = hashlib.sha256((data.sensor_id + data.payload).encode()).hexdigest()

    is_invalid = not validate_ecc(data.sensor_id, data.payload, data.ecc_signature)
    # is_invalid = data.ecc_signature != expected_sig
    message = "🔴 Spoofing attack simulated — ECC Signature Mismatch" if is_invalid else "✅ Signature appears valid"
    severity = "High" if is_invalid else "None"
    blocked = is_invalid
    persist_attack_log(data.sensor_id, "spoofing", message, severity)
    return {"timestamp": datetime.utcnow().isoformat(), "sensor_id": data.sensor_id, "attack_type": "spoofing",
            "message": message, "severity": severity, "blocked": blocked}


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
    persist_attack_log(req.sensor_id, "replay", message, severity)
    return {"timestamp": datetime.utcnow().isoformat(), "sensor_id": req.sensor_id, "attack_type": "replay",
            "message": message, "severity": severity, "blocked": blocked}


@router.post("/simulate/firmware")
async def simulate_firmware_attack(data: FirmwareUpload):
    await validate_sensor_id(data.sensor_id)
    is_valid_signature = data.firmware_signature == "valid_signature_123"
    message = "🔴 Firmware Rejected — Invalid Signature" if not is_valid_signature else "✅ Firmware Verified"
    severity = "High" if not is_valid_signature else "None"
    blocked = not is_valid_signature
    persist_attack_log(data.sensor_id, "firmware_injection", message, severity)
    return {"timestamp": datetime.utcnow().isoformat(), "sensor_id": data.sensor_id,
            "attack_type": "firmware_injection", "message": message, "severity": severity, "blocked": blocked}


@router.post("/simulate/ml_evasion")
async def simulate_ml_evasion_attack(data: SensorReading):
    await validate_sensor_id(data.sensor_id)
    readings = np.array(data.values).reshape(-1, 1)
    preds = model.predict(readings)
    is_drift = -1 in preds
    message = "🔴 ML Evasion Attempt — Drift Detected" if is_drift else "✅ Sensor Stable — No Drift"
    severity = "High" if is_drift else "None"
    blocked = is_drift
    persist_attack_log(data.sensor_id, "ml_evasion", message, severity)
    return {"timestamp": datetime.utcnow().isoformat(), "sensor_id": data.sensor_id, "attack_type": "ml_evasion",
            "message": message, "severity": severity, "blocked": blocked}


@router.post("/simulate/sensor_hijack")
async def simulate_sensor_hijack(data: AttackRequest):
    await validate_sensor_id(data.sensor_id)
    message = "🔴 Sensor Hijack Attempt — Stream Manipulated"
    severity = "High"
    blocked = True
    persist_attack_log(data.sensor_id, "sensor_hijack", message, severity)
    return {"timestamp": datetime.utcnow().isoformat(), "sensor_id": data.sensor_id, "attack_type": "sensor_hijack",
            "message": message, "severity": severity, "blocked": blocked}


@router.post("/simulate/api_abuse")
async def simulate_api_abuse(data: AttackRequest):
    await validate_sensor_id(data.sensor_id)
    message = "🔴 API Abuse Detected — Unauthorized Access Pattern"
    severity = "High"
    blocked = True
    persist_attack_log(data.sensor_id, "api_abuse", message, severity)
    return {"timestamp": datetime.utcnow().isoformat(), "sensor_id": data.sensor_id, "attack_type": "api_abuse",
            "message": message, "severity": severity, "blocked": blocked}


@router.post("/simulate/tamper_breach")
async def simulate_tamper_breach(data: AttackRequest):
    await validate_sensor_id(data.sensor_id)
    message = "🔴 Tamper Breach — Physical Layer Compromised"
    severity = "High"
    blocked = True
    persist_attack_log(data.sensor_id, "tamper_breach", message, severity)
    return {"timestamp": datetime.utcnow().isoformat(), "sensor_id": data.sensor_id, "attack_type": "tamper_breach",
            "message": message, "severity": severity, "blocked": blocked}


@router.post("/simulate/side_channel")
async def simulate_side_channel(data: AttackRequest):
    await validate_sensor_id(data.sensor_id)
    message = "🔴 Side-Channel Leak — Timing/Data Access Exploited"
    severity = "High"
    blocked = True
    persist_attack_log(data.sensor_id, "side_channel", message, severity)
    return {"timestamp": datetime.utcnow().isoformat(), "sensor_id": data.sensor_id, "attack_type": "side_channel",
            "message": message, "severity": severity, "blocked": blocked}


#### Sharp Explanation

@router.post("/api/shap/explain")
async def explain_shap(request: Request):
    try:
        data = await request.json()
        features = np.array([[v for v in data.values() if isinstance(v, (int, float))]])
        feature_names = [k for k, v in data.items() if isinstance(v, (int, float))]

        explainer = shap.Explainer(model)
        shap_values = explainer(features)

        result = {
            "prediction": str(model.predict(features)[0]),
            "base_value": float(shap_values.base_values[0]),
            "features": [
                {"feature": fname, "contribution": float(contrib)}
                for fname, contrib in zip(feature_names, shap_values.values[0])
            ]
        }
        return result
    except Exception as e:
        logger.exception("Failed to explain SHAP")
        raise HTTPException(status_code=500, detail="Error generating explanation")


@router.get("/api/shap-explanation/{image_name}")
def get_shap_image(image_name: str):
    try:
        file_path = os.path.join("shap_images", image_name)
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Explanation not found")
        return FileResponse(file_path, media_type="image/png")
    except Exception as e:
        logger.exception("Failed to serve SHAP explanation")
        raise HTTPException(status_code=500, detail="Error serving explanation")


@router.post("/api/shap/force-plot")
async def generate_force_plot(request: Request):
    import shap
    import matplotlib.pyplot as plt
    import base64
    from io import BytesIO

    try:
        data = await request.json()
        features = np.array([[v for v in data.values() if isinstance(v, (int, float))]])
        explainer = shap.Explainer(model)
        shap_values = explainer(features)

        # Generate image
        plt.figure()
        shap.plots.force(shap_values[0], matplotlib=True, show=False)
        buf = BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        encoded = base64.b64encode(buf.read()).decode("utf-8")
        buf.close()
        plt.close()
        return {"image_base64": encoded}
    except Exception as e:
        logger.exception("Failed to generate SHAP force plot")
        raise HTTPException(status_code=500, detail="Error generating force plot")
