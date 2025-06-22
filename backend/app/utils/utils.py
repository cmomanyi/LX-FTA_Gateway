from app.auth.auth import verify_token
from fastapi import WebSocket, status

from collections import defaultdict
from datetime import datetime
import hashlib

# Track number of active connections per sensor type
active_connections = defaultdict(int)


async def authenticate_websocket(websocket: WebSocket):
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return None

    try:
        user = await verify_token(token)
        await websocket.accept()
        return user
    except Exception:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return None


def get_timestamp():
    return datetime.utcnow()


def hash_firmware(firmware: str) -> str:
    return hashlib.sha256(firmware.encode()).hexdigest()
