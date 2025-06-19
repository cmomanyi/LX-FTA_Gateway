# # ddos_target.py
# import re
# from collections import defaultdict
# from collections import deque
# from datetime import datetime, timedelta
# from typing import Dict, List
#
# import numpy as np
# from fastapi import APIRouter, Request, HTTPException, WebSocket, WebSocketDisconnect
#
# from app.simulate_attacks.FirmwareUpload import FirmwareUpload
# from app.simulate_attacks.attack_log import get_attack_logs, log_attack
# from app.simulate_attacks.attack_request import AttackRequest
# from app.simulate_attacks.ml_evasion_detector import SensorReading, model
# from app.simulate_attacks.replay_threat import ReplayRequest, is_fresh_timestamp, USED_NONCES
# from app.simulate_attacks.spoofing_threat import SpoofingRequest
#
# router = APIRouter()
#
# request_log = deque(maxlen=1000)  # Sliding window to check frequency
#
# # Dynamic pattern: e.g., soil_01, water_03, threat_05
# SENSOR_PATTERN = re.compile(r"^(soil|water|plant|atmospheric|threat)_0[1-5]$")
#
# # Store timestamps of requests per sensor
# ddos_window: Dict[str, List[datetime]] = defaultdict(list)
#
# # Simulate global websocket broadcast (you'd replace with actual connected sockets)
# active_websockets: List[WebSocket] = []
# connected_clients = []
#
#
# # connected_clients: List[WebSocket] = []
# # -------------------- Utility --------------------
# def is_valid_sensor_id(sensor_id: str) -> bool:
#     return bool(SENSOR_PATTERN.match(sensor_id))
#
#
# # -------------------- Endpoints --------------------
# @router.get("/api/sensor-types")
# def get_sensor_types():
#     return {
#         "sensor_types": ["soil", "water", "plant", "atmospheric", "threat"],
#         "sensor_ids": ["01", "02", "03", "04", "05"]
#     }
#
#
# @router.post("/sensor/threat/ddos")
# async def handle_ddos(request: Request):
#     data = await request.json()
#     sensor_id = data["sensor_id"]
#     threshold = data.get("threshold", 10)
#     now = datetime.utcnow()
#
#     # Append current request timestamp
#     ddos_window[sensor_id].append(now)
#
#     # Keep only requests from the last 10 seconds
#     ddos_window[sensor_id] = [
#         t for t in ddos_window[sensor_id]
#         if (now - t).total_seconds() <= 10
#     ]
#     request_count = len(ddos_window[sensor_id])
#
#     # ✅ DDoS DETECTED: if request count exceeds threshold
#     if request_count > threshold:
#         alert = {
#             "timestamp": now.isoformat(),
#             "sensor_id": sensor_id,
#             "attack_type": "ddos",
#             "message": f"DDoS attack detected — {request_count} requests (threshold: {threshold})",
#             "severity": "High",
#             "blocked": True
#         }
#         log_attack(sensor_id, "ddos", alert["message"], severity=alert["severity"])
#         await broadcast_alert(alert)
#         return alert
#
#     # ✅ NO DDoS
#     message = f"No DDoS detected — {request_count}/{threshold}"
#     log_attack(sensor_id, "ddos", message, severity="None")
#     return {
#         "status": message,
#         "message": message,
#         "severity": "None",
#         "blocked": False
#     }
#
#
# @router.get("/api/target")
# async def target_endpoint(request: Request):
#     client_ip = request.client.host
#     now = datetime.utcnow()
#     request_log.append((client_ip, now))
#
#     # Count requests from this IP in the last 5 seconds
#     recent = [t for ip, t in request_log if ip == client_ip and (now - t).total_seconds() < 5]
#     if len(recent) > 10:  # DDoS threshold (tune as needed)
#         return {"status": "Blocked", "reason": "Too many requests"}
#
#     return {"status": "OK", "message": "Request accepted"}
#
#
# @router.post("/api/validate")
# def spoofing_protection(req: SpoofingRequest):
#     if not is_valid_sensor_id(req.sensor_id):
#         raise HTTPException(status_code=400, detail="Invalid sensor ID")
#
#     expected = hashlib.sha256((req.sensor_id + req.payload).encode()).hexdigest()
#
#     if req.ecc_signature != expected:
#         message = "🔴 Spoofing Detected – ECC Signature Mismatch"
#         log_attack(req.sensor_id, "spoofing", message, severity="High")
#         return {
#             "status": message,
#             "message": message,
#             "severity": "High",
#             "blocked": True
#         }
#
#     message = "✅ Signature Verified"
#     log_attack(req.sensor_id, "spoofing", message, severity="None")
#     return {
#         "status": message,
#         "message": message,
#         "severity": "None",
#         "blocked": False
#     }
#
#
# @router.post("/api/replay-protect")
# def detect_replay(req: ReplayRequest):
#     if not is_valid_sensor_id(req.sensor_id):
#         raise HTTPException(status_code=400, detail="Invalid sensor ID")
#
#     if req.nonce in USED_NONCES:
#         message = "🔴 Replay Detected – Duplicate Nonce"
#         log_attack(req.sensor_id, "replay", message, severity="High")
#         return {
#             "status": message,
#             "message": message,
#             "severity": "High",
#             "blocked": True
#         }
#
#     if not is_fresh_timestamp(req.timestamp):
#         raise HTTPException(status_code=400, detail="Stale timestamp")
#
#     USED_NONCES.add(req.nonce)
#     message = "✅ Payload Accepted – Fresh Nonce"
#     log_attack(req.sensor_id, "replay", message, severity="None")
#     return {
#         "status": message,
#         "message": message,
#         "severity": "None",
#         "blocked": False
#     }
#
#
# @router.post("/api/drift-detect")
# def detect_drift(data: SensorReading):
#     readings = np.array(data.values).reshape(-1, 1)
#     preds = model.predict(readings)
#
#     if -1 in preds:
#         message = "🔴 ML Evasion Attempt – Drift Behavior Detected"
#         log_attack(data.sensor_id, "drift", message, severity="High")
#         return {
#             "status": message,
#             "message": message,
#             "severity": "High",
#             "blocked": True
#         }
#
#     message = "✅ Sensor Stable – No Drift"
#     log_attack(data.sensor_id, "drift", message, severity="None")
#     return {
#         "status": message,
#         "message": message,
#         "severity": "None",
#         "blocked": False
#     }
#
#
# @router.post("/api/detect/firmware_injection")
# async def detect_firmware_injection(data: FirmwareUpload):
#     # Simulate failed signature verification
#     if not data.firmware_signature or data.firmware_signature != "valid_signature_123":
#         message = "🔴 Firmware Rejected – Signature Invalid"
#         alert = {
#             "timestamp": datetime.utcnow().isoformat(),
#             "sensor_id": data.sensor_id,
#             "attack_type": "firmware_injection",
#             "message": message,
#             "severity": "High",
#             "blocked": True
#         }
#         log_attack(data.sensor_id, "firmware_injection", message, severity="High")
#         await broadcast_alert(alert)
#         return alert
#
#     # If valid (fallback case)
#     return {
#         "status": "✅ Firmware accepted and verified",
#         "severity": "None",
#         "blocked": False
#     }
#
#
# WHITELISTED_IDS = {"soil_01", "plant_02", "threat_01", "atmo_03", "water_01"}
#
#
# @router.post("/api/detect/sensor_hijack")
# async def detect_sensor_hijack(data: AttackRequest):
#     if data.sensor_id not in WHITELISTED_IDS:
#         message = "🔴 Sensor Hijack – Unknown ID Used"
#         alert = {
#             "timestamp": datetime.utcnow().isoformat(),
#             "sensor_id": data.sensor_id,
#             "attack_type": "sensor_hijack",
#             "message": message,
#             "severity": "High",
#             "blocked": True
#         }
#         log_attack(data.sensor_id, "sensor_hijack", message, severity="High")
#         await broadcast_alert(alert)
#         return alert
#
#     # Fallback if sensor ID is known (legit)
#     return {
#         "status": "✅ Sensor ID verified via whitelist",
#         "message": "Sensor recognized and allowed",
#         "severity": "None",
#         "blocked": False
#     }
#
#
# # Simulate rate-limiting memory store
# ABUSE_TRACKER = {}
#
#
# @router.post("/api/detect/api_abuse")
# async def detect_api_abuse(data: AttackRequest):
#     now = datetime.utcnow()
#     sensor_id = data.sensor_id
#
#     # Create rate record
#     if sensor_id not in ABUSE_TRACKER:
#         ABUSE_TRACKER[sensor_id] = []
#
#     ABUSE_TRACKER[sensor_id].append(now)
#
#     # Keep only requests within the last 30 seconds
#     ABUSE_TRACKER[sensor_id] = [
#         t for t in ABUSE_TRACKER[sensor_id]
#         if t > now - timedelta(seconds=30)
#     ]
#
#     if len(ABUSE_TRACKER[sensor_id]) > 5:  # Simulate rate-limit threshold
#         message = "🔴 API Abuse – Rate Limit Triggered"
#         alert = {
#             "timestamp": now.isoformat(),
#             "sensor_id": sensor_id,
#             "attack_type": "api_abuse",
#             "message": message,
#             "severity": "High",
#             "blocked": True
#         }
#         log_attack(sensor_id, "api_abuse", message, severity="High")
#         await broadcast_alert(alert)
#         return alert
#
#     return {
#         "status": "✅ Config Change Accepted",
#         "message": "Request within safe frequency",
#         "severity": "None",
#         "blocked": False
#     }
#
#
# import hashlib
#
#
# @router.post("/api/detect/tamper_breach")
# async def detect_tamper_breach(data: AttackRequest):
#     # Simulate original hash stored in secure element
#     ORIGINAL_CONFIG_HASH = "abc123xyz456"
#
#     # Let's pretend incoming configs have different hash
#     fake_config = f"{data.sensor_id}_malicious_override"
#     computed_hash = hashlib.sha256(fake_config.encode()).hexdigest()
#
#     if computed_hash != ORIGINAL_CONFIG_HASH:
#         message = "🔴 Tamper Alert – Config Breach Detected"
#         alert = {
#             "timestamp": datetime.utcnow().isoformat(),
#             "sensor_id": data.sensor_id,
#             "attack_type": "tamper_breach",
#             "message": message,
#             "severity": "High",
#             "blocked": True
#         }
#         log_attack(data.sensor_id, "tamper_breach", message, severity="High")
#         await broadcast_alert(alert)
#         return alert
#
#     return {
#         "status": "✅ Config verified",
#         "severity": "None",
#         "blocked": False
#     }
#
#
# import random
#
#
# @router.post("/api/detect/side_channel")
# async def detect_side_channel(data: AttackRequest):
#     # Simulate timing variation in crypto operations (in microseconds)
#     simulated_delay_us = random.randint(50, 200)
#
#     # Assume normal crypto takes 80–120us. Outside = suspicious.
#     if simulated_delay_us < 80 or simulated_delay_us > 120:
#         message = "🔴 Side-Channel Suspected – Timing Anomaly"
#         alert = {
#             "timestamp": datetime.utcnow().isoformat(),
#             "sensor_id": data.sensor_id,
#             "attack_type": "side_channel",
#             "message": message,
#             "severity": "High",
#             "blocked": True
#         }
#         log_attack(data.sensor_id, "side_channel", message, severity="High")
#         await broadcast_alert(alert)
#         return alert
#
#     return {
#         "status": f"✅ Timing Normal – {simulated_delay_us}μs",
#         "severity": "None",
#         "blocked": False
#     }
#
#
# @router.websocket("/ws/alerts")
# async def websocket_endpoint(websocket: WebSocket):
#     await websocket.accept()
#     connected_clients.append(websocket)
#     try:
#         while True:
#             await websocket.receive_text()  # keep connection alive
#     except WebSocketDisconnect:
#         connected_clients.remove(websocket)
#
#
# @router.get("/api/logs")
# def fetch_logs():
#     return {"logs": get_attack_logs()}
#
#
#
#
# @router.get("/trigger/{attack_type}")
# async def trigger_attack(attack_type: str):
#     timestamp = datetime.utcnow().isoformat()
#     sensor_id = "sim_sensor_01"
#
#     examples = {
#         "spoofing": {
#             "message": "🔴 Spoofing Detected – ECC Signature Mismatch",
#             "severity": "Medium",
#             "blocked": True
#         },
#         "replay": {
#             "message": "🔴 Replay Detected – Duplicate Nonce",
#             "severity": "Medium",
#             "blocked": True
#         },
#         "firmware": {
#             "message": "🔴 Firmware Rejected – Signature Invalid",
#             "severity": "High",
#             "blocked": True
#         },
#         "ml": {
#             "message": "🔴 ML Evasion Attempt – Drift Behavior Detected",
#             "severity": "High",
#             "blocked": True
#         },
#         "overflow": {
#             "message": "🔴 Buffer Overflow – Payload Length Exceeded",
#             "severity": "High",
#             "blocked": True
#         },
#         "ddos": {
#             "message": "🔴 DDoS attack detected — excessive requests",
#             "severity": "High",
#             "blocked": True
#         },
#         "api": {
#             "message": "🔴 API Abuse – Rate Limit Triggered",
#             "severity": "Medium",
#             "blocked": True
#         },
#         "sidechannel": {
#             "message": "🔴 Side-Channel Suspected – Timing Anomaly",
#             "severity": "High",
#             "blocked": True
#         },
#         "tamper": {
#             "message": "🔴 Tamper Alert – Config Breach Detected",
#             "severity": "High",
#             "blocked": True
#         },
#         "hijack": {
#             "message": "🔴 Sensor Hijack – Unknown ID Used",
#             "severity": "High",
#             "blocked": True
#         }
#     }
#
#     if attack_type not in examples:
#         return {"error": "Invalid attack type"}
#
#     alert = {
#         "timestamp": timestamp,
#         "sensor_id": sensor_id,
#         "attack_type": attack_type,
#         **examples[attack_type]
#     }
#
#     await broadcast_alert(alert)
#     return {"status": f"{attack_type.capitalize()} alert triggered"}
#
#
# # WebSocket broadcast
# async def broadcast_alert(alert: dict):
#     # disconnected = []
#     for ws in active_websockets:
#         try:
#             await ws.send_json(alert)
#         except:
#             connected_clients.append(ws)
#     for ws in connected_clients:
#         active_websockets.remove(ws)
