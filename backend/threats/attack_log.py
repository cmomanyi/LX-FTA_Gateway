# attack_log.py

from typing import List
from datetime import datetime

attack_logs: List[dict] = []


def log_attack(sensor_id: str, attack_type: str, message: str, severity: str = "High"):
    attack_logs.insert(0, {
        "timestamp": datetime.utcnow().isoformat(),
        "sensor_id": sensor_id,
        "attack_type": attack_type,
        "message": message,
        "severity": severity,
    })


def get_attack_logs() -> List[dict]:
    return attack_logs[:500]  # limit return for performance
