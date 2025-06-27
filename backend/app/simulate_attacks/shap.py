from fastapi import APIRouter
from fastapi.responses import JSONResponse
import shap
import numpy as np
from datetime import datetime
from app.simulate_attacks.ml_evasion_detector import model  # Pretrained IsolationForest or similar
from app.simulate_attacks.attack_log import get_attack_logs

router = APIRouter()

# Dummy mapping for feature names for demonstration
FEATURE_NAMES = ["sensor_id", "temperature", "moisture", "pH", "battery_level", "request_frequency"]


# Embed sensor ID as numeric encoding for SHAP use (mocked)
def encode_sensor_id(sensor_id: str) -> int:
    return abs(hash(sensor_id)) % 10000


@router.get("/api/shap/latest")
async def explain_latest_blocked():
    logs = get_attack_logs()
    blocked_logs = [log for log in reversed(logs) if log.get("blocked") and "sensor_id" in log]

    if not blocked_logs:
        return JSONResponse(status_code=404, content={"error": "No blocked attacks available for SHAP explanation."})

    latest = blocked_logs[0]
    sensor_id = latest["sensor_id"]
    attack_type = latest["attack_type"]

    # Simulate corresponding sensor input vector for SHAP
    encoded_id = encode_sensor_id(sensor_id)
    np.random.seed(encoded_id)  # Deterministic mock features
    input_features = np.array([
        encoded_id,  # encoded sensor ID
        np.random.uniform(20, 90),  # temperature
        np.random.uniform(0.1, 0.9),  # moisture
        np.random.uniform(4.0, 9.0),  # pH
        np.random.uniform(10, 100),  # battery level
        np.random.randint(1, 100)  # request frequency
    ])

    input_data = input_features.reshape(1, -1)
    explainer = shap.Explainer(model, masker=shap.maskers.Independent(input_data))
    shap_values = explainer(input_data)

    # Extract contributions
    contribs = dict(zip(FEATURE_NAMES, shap_values.values[0].tolist()))
    total_score = sum(shap_values.values[0])

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "sensor_id": sensor_id,
        "attack_type": attack_type,
        "contributions": contribs,
        "total_score": total_score
    }
