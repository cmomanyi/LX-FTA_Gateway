from fastapi import APIRouter, HTTPException, Depends, WebSocketException, status
from pydantic import BaseModel
from datetime import datetime, timedelta
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
import logging

# Setup logging
logger = logging.getLogger("auth")
logger.setLevel(logging.INFO)

router = APIRouter()
security = HTTPBearer()

ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 60

# Hardcoded credentials and secret
AUTH_DATA = {
    "admin": {
        "password": "admin123",
        "role": "admin"
    },
    "analyst": {
        "password": "analyst123",
        "role": "analyst"
    },
    "sensor": {
        "password": "sensor123",
        "role": "sensor"
    },
    "jwt_secret": "pkybZBce_EP-RppbW4y0DYxljiDvyPLs8tU9Vm1ezY8"
}

class LoginRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

def create_access_token(data: dict, expires_delta: timedelta = None):
    secret_key = AUTH_DATA.get("jwt_secret")
    if not secret_key:
        raise RuntimeError("JWT secret is missing.")
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, secret_key, algorithm=ALGORITHM)

async def verify_token(token: str):
    secret_key = AUTH_DATA.get("jwt_secret")
    if not secret_key:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)

    try:
        payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
        return username
    except JWTError as e:
        logger.warning(f"JWT validation failed: {e}")
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)

@router.post("/login", response_model=Token)
def login(req: LoginRequest):
    user = AUTH_DATA.get(req.username)
    if not user or user["password"] != req.password:
        logger.warning(f"Failed login attempt for user: {req.username}")
        raise HTTPException(status_code=401, detail="Invalid username or password.")
    token = create_access_token(
        {"sub": req.username, "role": user["role"]},
        timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    )
    logger.info(f"User {req.username} authenticated successfully.")
    return {"access_token": token, "token_type": "bearer"}

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    secret_key = AUTH_DATA.get("jwt_secret")
    try:
        payload = jwt.decode(credentials.credentials, secret_key, algorithms=[ALGORITHM])
        return {"username": payload.get("sub"), "role": payload.get("role")}
    except JWTError:
        logger.error("Token validation failed.")
        raise HTTPException(status_code=403, detail="Invalid token.")

def require_role(role: str):
    def role_checker(user=Depends(get_current_user)):
        if user["role"] != role:
            raise HTTPException(status_code=403, detail="Access forbidden.")
        return user
    return role_checker

@router.get("/protected")
def protected_route(user: dict = Depends(get_current_user)):
    return {"message": f"Hello {user['username']}, you have {user['role']} access."}

@router.get("/secrets-health")
def secrets_health_check():
    if "jwt_secret" not in AUTH_DATA:
        raise HTTPException(status_code=500, detail="JWT secret not found.")
    return {"status": "ok", "message": "Hardcoded secrets are accessible."}
