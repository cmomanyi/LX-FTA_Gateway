import asyncio
import random
from datetime import datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from fastapi.responses import JSONResponse
from app.websocket_socket_types import generate_sensor_data
from auth.auth import verify_token
from utils.utils import authenticate_websocket, active_connections  # or use .websocket_routes if in same file
import logging

from jose import jwt

router = APIRouter()

logger = logging.getLogger("sensor_gateway")
logging.basicConfig(level=logging.INFO)

VALID_SENSOR_TYPES = {"soil", "water", "threat", "atmospheric", "plant"}
ATTACK_TYPES = ["spoofing", "replay", "firmware injection", "ML evasion", "API abuse", "side-channel timing"]
SENSOR_TYPES = ["soil", "water", "plant", "threat", "atmospheric"]


@router.websocket("/ws/soil")
async def soil_data_stream(websocket: WebSocket):
    user = await authenticate_websocket(websocket)
    if not user:
        return
    try:
        while True:
            data = {
                "sensor_id": f"soil-{random.randint(1000, 9999)}",
                "user": user,
                "temperature": round(random.uniform(15.0, 35.0), 2),
                "moisture": round(random.uniform(20.0, 80.0), 2),
                "status": random.choice(["active", "sleeping", "compromised"]),
            }
            await websocket.send_json(data)
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        print("Soil sensor client disconnected")


@router.websocket("/ws/water")
async def water_data_stream(websocket: WebSocket):
    user = await authenticate_websocket(websocket)
    if not user:
        return
    try:
        while True:
            data = {
                "sensor_id": f"water-{random.randint(1000, 9999)}",
                "user": user,
                "flow_rate": round(random.uniform(5.0, 15.0), 2),
                "water_level": round(random.uniform(10.0, 45.0), 2),
                "status": random.choice(["active", "compromised"]),
            }
            await websocket.send_json(data)
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        print("Water sensor client disconnected")


@router.websocket("/ws/threat")
async def threat_data_stream(websocket: WebSocket):
    user = await authenticate_websocket(websocket)
    if not user:
        return
    try:
        while True:
            data = {
                "sensor_id": f"threat-{random.randint(1000, 9999)}",
                "user": user,
                "anomaly_score": round(random.uniform(0.0, 1.0), 2),
                "tampering": random.choice([True, False]),
                "jamming": random.choice([True, False]),
                "status": random.choice(["active", "alert"]),
            }
            await websocket.send_json(data)
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        print("Threat sensor client disconnected")


@router.websocket("/ws/atmospheric")
async def atmospheric_data_stream(websocket: WebSocket):
    user = await authenticate_websocket(websocket)
    if not user:
        return
    try:
        while True:
            data = {
                "sensor_id": f"atm-{random.randint(1000, 9999)}",
                "user": user,
                "air_temp": round(random.uniform(10.0, 40.0), 2),
                "humidity": round(random.uniform(30.0, 90.0), 2),
                "co2": round(random.uniform(300.0, 600.0), 2),
                "status": random.choice(["active", "error"]),
            }
            await websocket.send_json(data)
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        print("Atmospheric sensor client disconnected")


@router.websocket("/ws/plant")
async def plant_data_stream(websocket: WebSocket):
    user = await authenticate_websocket(websocket)
    if not user:
        return
    try:
        while True:
            data = {
                "sensor_id": f"plant-{random.randint(1000, 9999)}",
                "user": user,
                "chlorophyll": round(random.uniform(20.0, 50.0), 2),
                "leaf_moisture": round(random.uniform(30.0, 70.0), 2),
                "growth_rate": round(random.uniform(0.5, 2.0), 2),
                "status": random.choice(["healthy", "wilting", "diseased"]),
            }
            await websocket.send_json(data)
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        print("Plant sensor client disconnected")


@router.websocket("/ws/alerts")
async def alert_stream(websocket: WebSocket):
    user = await authenticate_websocket(websocket)
    if not user:
        return
    try:
        while True:
            alert = {
                "time": datetime.now().strftime("%H:%M:%S"),
                "sensor": f"{random.choice(SENSOR_TYPES)}-{random.randint(1000, 9999)}",
                "type": random.choice(ATTACK_TYPES),
                "severity": "high",
                "status": "breached",
                "user": user,
            }
            await websocket.send_json(alert)
            await asyncio.sleep(3)

    except WebSocketDisconnect:
        print("Alert stream disconnected.")
    except Exception as e:
        print("Connection rejected due to:", str(e))
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)


# @router.websocket("/ws/{sensor_type}")
# async def generic_sensor_ws(websocket: WebSocket, sensor_type: str):
#     if sensor_type not in VALID_SENSOR_TYPES:
#         await websocket.close(code=status.WS_1003_UNSUPPORTED_DATA)
#         return
#
#     token = websocket.query_params.get("token")
#     if not token:
#         await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
#         return
#
#     try:
#         user = await verify_token(token)
#         await websocket.accept()
#
#         while True:
#             data = generate_sensor_data(sensor_type, user)
#             await websocket.send_json(data)
#             await asyncio.sleep(2)
#
#     except WebSocketDisconnect:
#         print(f"{sensor_type.capitalize()} sensor client disconnected")
#     except Exception as e:
#         print(f"Error in {sensor_type} WebSocket:", str(e))
#         await websocket.close(code=status.WS_1011_INTERNAL_ERROR)


@router.websocket("/ws/{sensor_type}")
async def generic_sensor_ws(websocket: WebSocket, sensor_type: str):
    if sensor_type not in VALID_SENSOR_TYPES:
        await websocket.close(code=status.WS_1003_UNSUPPORTED_DATA)
        return

    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    try:
        user = await verify_token(token)
        await websocket.accept()

        # Log and track new connection
        active_connections[sensor_type] += 1
        logger.info(f"[{sensor_type.upper()}] Connected: {user} | Active: {active_connections[sensor_type]}")

        while True:
            data = generate_sensor_data(sensor_type, user)
            await websocket.send_json(data)
            await asyncio.sleep(2)

    except WebSocketDisconnect:
        logger.info(f"[{sensor_type.upper()}] Disconnected: {user}")
    except Exception as e:
        logger.error(f"[{sensor_type.upper()}] Error: {str(e)}")
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
    finally:
        # Ensure we decrement even on error
        if active_connections[sensor_type] > 0:
            active_connections[sensor_type] -= 1
            logger.info(f"[{sensor_type.upper()}] Remaining connections: {active_connections[sensor_type]}")


#
# @router.websocket("/ws/alerts")
# async def alert_stream(websocket: WebSocket):
#     token = websocket.query_params.get("token")
#     if not token:
#         await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
#         return
#     try:
#         user = await verify_token(token)
#         await websocket.accept()
#
#         while True:
#             alert = {
#                 "time": datetime.now().strftime("%H:%M:%S"),
#                 "sensor": f"{random.choice(SENSOR_TYPES)}-{random.randint(1000, 9999)}",
#                 "type": random.choice(ATTACK_TYPES),
#                 "severity": "high",
#                 "status": "breached",
#             }
#             await websocket.send_json(alert)
#             await asyncio.sleep(3)
#     except WebSocketDisconnect:
#         print("Alert stream disconnected.")

# @router.websocket("/ws/alerts")
# async def alert_stream(websocket: WebSocket):
#     token = websocket.query_params.get("token")
#     claims = jwt.get_unverified_claims(token)
#     print(claims)
#     if not token:
#         await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
#         return
#
#     try:
#         user = await verify_token(token)
#         await websocket.accept()
#
#         while True:
#             alert = {
#                 "time": datetime.now().strftime("%H:%M:%S"),
#                 "sensor": f"{random.choice(SENSOR_TYPES)}-{random.randint(1000, 9999)}",
#                 "type": random.choice(ATTACK_TYPES),
#                 "severity": "high",
#                 "status": "breached",
#                 "user": user,
#             }
#             await websocket.send_json(alert)
#             await asyncio.sleep(3)
#
#     except WebSocketDisconnect:
#         print("Alert stream disconnected.")
#     except Exception as e:
#         print("Connection rejected due to:", str(e))
#         await websocket.close(code=status.WS_1008_POLICY_VIOLATION)


@router.get("/metrics/connections")
async def get_connection_metrics():
    return JSONResponse(content=dict(active_connections))
