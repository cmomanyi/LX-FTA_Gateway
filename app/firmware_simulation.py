from fastapi import UploadFile, Form, File, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from datetime import datetime
import hashlib
import random

router = APIRouter()

# Mock trusted issuers and known hashes
trusted_issuers = ["Trusted_CA_01", "Trusted_CA_02"]
known_hashes = ["abc123", "def456", "ghi789"]

# Simulated audit log (in-memory)
firmware_log = []


@router.post("/api/firmware/upload")
async def simulate_firmware_upload(
        file: UploadFile = File(...),
        firmwareVersion: str = Form(...),
        issuerId: str = Form(...),
        targetDevice: str = Form(...),
        deploymentDate: str = Form(...),
        attemptDowngrade: bool = Form(False)
):
    simulated_hash = random.choice(known_hashes + ["tampered123"])
    is_known_hash = simulated_hash in known_hashes
    is_trusted_issuer = issuerId in trusted_issuers
    current_version = "v3.0.5"
    downgrade_attempted = attemptDowngrade and firmwareVersion < current_version

    if downgrade_attempted:
        status_msg = "🚫 Deployment blocked. Rollback protection activated."
        status = "Rejected"
    elif not is_trusted_issuer:
        status_msg = "❌ Firmware rejected: Unknown issuer"
        status = "Rejected"
    elif not is_known_hash:
        status_msg = "⚠️ Firmware tampered: Hash mismatch"
        status = "Rejected"
    else:
        status_msg = "✅ Firmware verified and accepted"
        status = "Verified"

    audit_hash = hashlib.sha256(
        f"{firmwareVersion}{issuerId}{datetime.utcnow()}".encode()
    ).hexdigest()

    log_entry = {
        "event": "Firmware Upload",
        "version": firmwareVersion,
        "issuer": issuerId,
        "status": status,
        "timestamp": datetime.utcnow().isoformat(),
        "audit_hash": audit_hash,
        "hash": simulated_hash,
        "target_device": targetDevice,
        "deployment_date": deploymentDate
    }

    firmware_log.append(log_entry)

    return JSONResponse(content={**log_entry, "message": status_msg})


@router.get("/api/sample-firmware")
def download_sample_firmware():
    content = (
        "# Mock Firmware Binary File\n"
        "# Firmware Version: v3.0.5\n"
        "# Target Device: soil_sensor_alpha\n"
        "# Issuer: Trusted_CA_01\n"
        "# Payload: Simulated binary block\n\n"
        "0000111122223333444455556666777788889999AAAAFFFFEEEEDDDDCCCCBBBB0000"
    )
    return Response(
        content=content,
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": "attachment; filename=mock_firmware_v3.0.5.bin"
        }
    )


@router.get("/api/firmware/log")
def get_firmware_log():
    return firmware_log[::-1]
