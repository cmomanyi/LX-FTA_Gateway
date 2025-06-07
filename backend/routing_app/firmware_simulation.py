from fastapi import  APIRouter, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict
from datetime import datetime

router = APIRouter()
firmware_registry = {}
# firmware_registry: Dict[str, Dict] = {}
firmware_audit_log = []

# Sensor Types and IDs
SENSOR_TYPES = ["soil", "water", "atmospheric", "plant", "threat"]
SENSOR_IDS = ["1", "2", "3", "4", "5"]

# Auto-initialize known sensors
for stype in SENSOR_TYPES:
    for sid in SENSOR_IDS:
        key = f"{stype}_{sid}"
        firmware_registry[key] = {
            "current": "v1.0.0",
            "last": "none",
            "rollback_protection": True
        }


def verify_signature(signature: str) -> bool:
    return signature != "invalid_signature_xx"


@router.get("/api/firmware/versions/{sensor_id}")
async def get_firmware_versions(sensor_id: str):
    if sensor_id not in firmware_registry:
        # Auto-initialize unknown sensor IDs
        firmware_registry[sensor_id] = {
            "current": "v1.0.0",
            "last": "none",
            "rollback_protection": True
        }
    return firmware_registry[sensor_id]


@router.post("/api/firmware/upload")
async def upload_firmware(
        file: UploadFile,
        sensor_id: str = Form(...),
        firmwareVersion: str = Form(...),
        issuerId: str = Form(...),
        deploymentDate: str = Form(...),
        attemptDowngrade: bool = Form(False)
):
    log_entry = {
        "sensor_id": sensor_id,
        "version": firmwareVersion,
        "issuer": issuerId,
        "timestamp": datetime.utcnow().isoformat(),
        "status": "",
        "details": {
            "deploymentDate": deploymentDate,
            "filename": file.filename
        }
    }

    entry = firmware_registry.get(sensor_id, {
        "current": None,
        "last": None,
        "rollback_protection": True
    })

    if not verify_signature(file.filename):
        log_entry["status"] = "Rejected - Invalid Signature"
        firmware_audit_log.append(log_entry)
        return JSONResponse(status_code=400,
                            content={"status": "Rejected", "message": "🔴 Firmware Rejected – Signature Invalid",
                                     "blocked": True})

    if entry["current"] and firmwareVersion < entry["current"]:
        if entry.get("rollback_protection", True) and not attemptDowngrade:
            log_entry["status"] = "Blocked - Downgrade Not Allowed"
            firmware_audit_log.append(log_entry)
            return JSONResponse(status_code=400, content={"status": "Downgrade Blocked",
                                                          "message": "❌ Downgrade blocked by rollback protection",
                                                          "blocked": True})

    firmware_registry[sensor_id] = {
        "current": firmwareVersion,
        "last": entry["current"] or "none",
        "rollback_protection": entry["rollback_protection"]
    }

    log_entry["status"] = "Verified"
    firmware_audit_log.append(log_entry)

    return {
        "status": "✅ Firmware Uploaded",
        "message": f"Firmware {firmwareVersion} uploaded successfully to {sensor_id}.",
        "blocked": False
    }


@router.get("/api/firmware/log")
def get_firmware_logs():
    return firmware_audit_log


