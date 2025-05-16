from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from pydantic import BaseModel
from typing import List, Dict, Any
import json

from auth.auth import SECRET_KEY, ALGORITHM, require_role

router = APIRouter()
security = HTTPBearer()

# Dummy JWT validation and role enforcement
# def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
#     token = credentials.credentials
#     # For demo: decode JWT (in real case, use PyJWT)
#     if "admin" not in token:
#         raise HTTPException(status_code=403, detail="Admin access required")
#     return token


# ---------- Anomaly Logs ----------
anomaly_logs = [
    {"time": "2025-05-15T12:30:45Z", "sensor": "soil-003", "type": "spoofing", "severity": "High"},
    {"time": "2025-05-15T12:35:10Z", "sensor": "water-002", "type": "signal_loss", "severity": "Medium"}
]


def get_current_admin(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=403, detail="Authorization header missing or invalid format")

    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError as e:
        raise HTTPException(status_code=403, detail=f"Token decode error: {str(e)}")

    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="User is not an admin")

    return payload  # You can return more user info here if needed


@router.get("/api/anomalies")
def get_anomalies(admin=Depends(get_current_admin)):
    return anomaly_logs


# ---------- Policy-as-Code ----------
class PolicyInput(BaseModel):
    policy: Dict[str, Any]


@router.get("/api/policy")
def get_policy(admin=Depends(get_current_admin)):
    return {"policy": {"access": {"roles": ["admin"]}}}


@router.post("/api/policy/validate")
def validate_policy(input: PolicyInput, admin=Depends(get_current_admin)):
    try:
        json.dumps(input.policy)
        return {"message": "Valid policy"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/api/policy/simulate")
def simulate_policy(input: PolicyInput, admin=Depends(get_current_admin)):
    return {"message": "Simulation passed", "sample_effect": "Access granted"}


@router.post("/api/policy/deploy")
def deploy_policy(input: PolicyInput, admin=Depends(get_current_admin)):
    print("Logging to blockchain...", input.policy)
    return {"message": "Policy deployed"}


# ---------- Firmware Update ----------
@router.post("/api/firmware/update")
def upload_firmware(
        file: UploadFile = File(...),
        simulate_tamper: bool = Form(...),
        admin=Depends(get_current_admin)
):
    filename = file.filename
    if simulate_tamper or "unsigned" in filename or "v1.0" in filename:
        return {"status": "rejected", "reason": "tampered or outdated"}
    return {"status": "accepted", "version": filename}
