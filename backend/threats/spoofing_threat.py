from pydantic import BaseModel
import hashlib

# -----------------------
# Spoofing Detection Logic
# -----------------------
AUTHORIZED_SENSORS = {
    "sensor-001": "valid_signature_abc123",
    "sensor-002": "valid_signature_def456"
}


# Example reused in spoofing/replay routes
class SpoofingRequest(BaseModel):
    sensor_id: str
    payload: str
    ecc_signature: str


def validate_ecc(sensor_id: str, payload: str, signature: str) -> bool:
    """
    Dummy ECC signature validator
    For real systems, use cryptography.ecc or similar.
    """
    # Simulate correct signature by hashing payload
    valid_signature = hashlib.sha256((sensor_id + payload).encode()).hexdigest()
    return signature == valid_signature
