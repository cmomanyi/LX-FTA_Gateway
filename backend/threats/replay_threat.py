from typing import Set

from pydantic import BaseModel
from datetime import datetime, timedelta

# -----------------------------
# Replay Protection Structures
# -----------------------------
USED_NONCES: Set[str] = set()
NONCE_EXPIRY_SECONDS = 30


class ReplayRequest(BaseModel):
    sensor_id: str
    payload: str
    timestamp: str  # ISO format
    nonce: str


def is_fresh_timestamp(ts: str) -> bool:
    try:
        sent_time = datetime.fromisoformat(ts)
        now = datetime.utcnow()
        return abs((now - sent_time).total_seconds()) < NONCE_EXPIRY_SECONDS
    except ValueError:
        return False
