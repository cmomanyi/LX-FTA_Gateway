import json
from datetime import datetime
import hashlib

used_nonces = set()
firmware_hash = None
API_LOG_WINDOW = []

AUTHORIZED_SENSORS = {"soil_01", "plant_02", "threat_01", "atmo_03"}
ORIGINAL_CONFIG_HASH = "abc123xyz456"  # Stored at LX-FTA boot


def get_timestamp():
    return datetime.utcnow().isoformat() + "Z"


def log_attack(attack_type, message, severity="High", sensor_id=None, target="unspecified"):
    entry = {
        "timestamp": get_timestamp(),
        "attack_type": attack_type,
        "message": message,
        "status": "Blocked",
        "severity": severity,
        "target": target
    }
    if sensor_id:
        entry["sensor_id"] = sensor_id
    with open("security_events_log.json", "a") as f:
        f.write(json.dumps(entry) + "\n")
    return entry


# 1. Spoofing – ECC Signature Mismatch
def detect_spoofing(is_signature_valid, sensor_id):
    if not is_signature_valid:
        return log_attack("Spoofing", "ECC Signature mismatch", sensor_id=sensor_id, target="sensor")
    return None


# 2. Replay Attack – Reused Nonce or Expired Timestamp
def detect_replay(timestamp, nonce, sensor_id):
    now = datetime.utcnow()
    if nonce in used_nonces or abs((now - timestamp).total_seconds()) > 30:
        return log_attack("Replay Attack", "Old or duplicate nonce/timestamp", sensor_id=sensor_id, target="sensor")
    used_nonces.add(nonce)
    return None


# 3. Firmware Injection – Hash Mismatch on Update
def detect_firmware_tampering(current_hash, sensor_id):
    global firmware_hash
    if firmware_hash is None:
        firmware_hash = current_hash
    elif current_hash != firmware_hash:
        return log_attack("Firmware Injection", "Firmware hash mismatch", sensor_id=sensor_id, target="gateway")
    return None


# 4. ML Evasion – Anomalous AI Confidence
def detect_ml_evasion(model_confidence, sensor_id):
    if model_confidence < 0.3:
        return log_attack("ML Evasion", "Adversarial input detected from sensor data", sensor_id=sensor_id,
                          target="gateway")
    return None


# 5. Buffer Overflow – Oversized Payload from Sensor
def detect_overflow(input_payload, sensor_id):
    if len(input_payload) > 1024:
        return log_attack("Overflow Attack", "Input size exceeds allowed limit", sensor_id=sensor_id, target="sensor")
    return None


# 6. DDoS – Excessive API Requests from Gateway
def detect_ddos(sensor_id=None):
    from datetime import datetime
    now = datetime.utcnow()
    API_LOG_WINDOW.append(now)
    while API_LOG_WINDOW and (now - API_LOG_WINDOW[0]).total_seconds() > 60:
        API_LOG_WINDOW.pop(0)
    if len(API_LOG_WINDOW) > 20:
        return log_attack("DDoS", "Excessive requests to cloud API", sensor_id=sensor_id, target="API")
    return None


# 7. API Abuse – Unauthorized Endpoint Access Attempt
def detect_api_abuse(user_role, endpoint, sensor_id=None):
    if user_role != "admin" and endpoint in ["/firmware-update", "/shutdown"]:
        return log_attack("API Abuse", f"Unauthorized access attempt to {endpoint}", sensor_id=sensor_id, target="API")
    return None


# 8. Side-Channel Attack – Timing/Power Variance Detected
def detect_side_channel(cpu_time, power_usage, sensor_id):
    if cpu_time > 0.9 and power_usage > 0.9:
        return log_attack("Side-Channel Attack", "High timing and power usage correlation", sensor_id=sensor_id,
                          target="gateway")
    return None


# 9. Tamper Breach – Config File Integrity Failure
def detect_tamper_breach(current_config_hash, sensor_id=None):
    if current_config_hash != ORIGINAL_CONFIG_HASH:
        return log_attack("Tamper Breach", "Config file hash mismatch detected", sensor_id=sensor_id, target="gateway")
    return None


# 10. Sensor Hijack – Unauthorized Sensor ID
def detect_sensor_hijack(sensor_id):
    if sensor_id not in AUTHORIZED_SENSORS:
        return log_attack("Sensor Hijack", f"Unauthorized sensor ID '{sensor_id}'", sensor_id=sensor_id,
                          target="sensor")
    return None
