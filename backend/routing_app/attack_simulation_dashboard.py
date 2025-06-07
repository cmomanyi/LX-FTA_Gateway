# main.py (FastAPI backend for LX-FTA Attack Simulation)

from fastapi import APIRouter, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import random
import uuid

router = APIRouter()

# In-memory attack log
attack_log = []


# Mock simulator functions
def log_attack(attack_type, result):
    timestamp = datetime.utcnow().isoformat()
    log = {
        "timestamp": timestamp,
        "attack_type": attack_type,
        "status": result["status"],
        "message": result["message"],
        "sensor_id": result.get("sensor_id", f"sensor_{random.randint(100, 999)}"),
        "severity": "High"
    }
    attack_log.append(log)
    return log


def simulate_spoofing():
    result = {"status": "Blocked", "message": "ECC Signature Mismatch", "sensor_id": "sensor_257"}
    return log_attack("spoofing", result)


def simulate_replay_attack():
    result = {"status": "Blocked", "message": "Old Nonce Reused", "sensor_id": "sensor_174"}
    return log_attack("replay", result)


def simulate_ml_evasion():
    result = {"status": "Blocked", "message": "Anomaly Drift Detected", "sensor_id": "sensor_389"}
    return log_attack("ml_evasion", result)


def simulate_firmware_injection():
    result = {"status": "Blocked", "message": "Unsigned Firmware Detected", "sensor_id": "sensor_401"}
    return log_attack("firmware_injection", result)


def simulate_sensor_hijack():
    result = {"status": "Blocked", "message": "Unknown Sensor ID", "sensor_id": "sensor_999"}
    return log_attack("sensor_hijack", result)


def simulate_api_abuse():
    result = {"status": "Blocked", "message": "Rate Limit Exceeded", "sensor_id": "sensor_322"}
    return log_attack("api_abuse", result)


def simulate_tamper_breach():
    result = {"status": "Breached", "message": "Gateway Configuration Tampered", "sensor_id": "sensor_005"}
    return log_attack("tamper_breach", result)


def simulate_side_channel():
    result = {"status": "Breached", "message": "Timing Anomaly in Crypto", "sensor_id": "sensor_778"}
    return log_attack("side_channel", result)


def simulate_ddos_flood():
    result = {"status": "Blocked", "message": "DDoS Attempt Detected", "sensor_id": "sensor_900"}
    return log_attack("ddos_flood", result)


# Route to simulate an attack
@router.post("/simulate-attack")
def simulate_attack(attack_type: str = Form(...)):
    simulations = {
        "spoofing": simulate_spoofing,
        "replay": simulate_replay_attack,
        "ml_evasion": simulate_ml_evasion,
        "firmware_injection": simulate_firmware_injection,
        "sensor_hijack": simulate_sensor_hijack,
        "api_abuse": simulate_api_abuse,
        "tamper_breach": simulate_tamper_breach,
        "side_channel": simulate_side_channel,
        "ddos_flood": simulate_ddos_flood
    }
    if attack_type not in simulations:
        raise HTTPException(status_code=400, detail="Invalid attack type")
    return JSONResponse(content=simulations[attack_type]())


# Route to fetch attack log
@router.get("/attack-log")
def get_attack_log():
    return attack_log
