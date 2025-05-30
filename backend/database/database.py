from typing import List
import json
from backend.models.models import AnomalyLog

anomaly_logs: List[AnomalyLog] = []
used_nonces = set()

LOG_FILE = "logs.json"


def save_to_disk(log: AnomalyLog):
    try:
        with open(LOG_FILE, "r") as f:
            existing = json.load(f)
    except:
        existing = []

    existing.insert(0, log.dict())
    with open(LOG_FILE, "w") as f:
        json.dump(existing, f, indent=2)
