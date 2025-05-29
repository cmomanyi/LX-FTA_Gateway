from models.models import SensorData, AnomalyLog
from utils.utils import get_timestamp
from database.database import used_nonces, anomaly_logs
from database.database import save_to_disk

AUTHORIZED_SENSORS = {"soil_01", "plant_02", "threat_01"}


def detect_spoofing(data: SensorData) -> AnomalyLog:
    if data.sensor_id not in AUTHORIZED_SENSORS:
        return AnomalyLog(
            timestamp=get_timestamp(),
            sensor_id=data.sensor_id,
            attack_type="Spoofing",
            message="Unauthorized sensor ID",
            severity="High",
            status="blocked"
        )


def detect_replay(data: SensorData) -> AnomalyLog:
    if data.nonce in used_nonces:
        return AnomalyLog(
            timestamp=get_timestamp(),
            sensor_id=data.sensor_id,
            attack_type="Replay",
            message="Duplicate nonce detected",
            severity="Medium",
            status="blocked"
        )
    used_nonces.add(data.nonce)


# Example usage:
# if log1:
#     anomaly_logs.append(log1)
#     save_to_disk(log1)
