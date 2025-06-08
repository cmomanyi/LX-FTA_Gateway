from fastapi import APIRouter, HTTPException, Depends, WebSocketException, status
from pydantic import BaseModel
from datetime import datetime, timedelta
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from functools import lru_cache
from dotenv import load_dotenv
import boto3
import os
import json
import logging

# Load .env (useful for local dev)
load_dotenv()

# Setup logging
logger = logging.getLogger("auth")
logger.setLevel(logging.INFO)

router = APIRouter()
security = HTTPBearer()

ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 60

# Load environment variables
REGION = os.getenv("AWS_REGION", "us-east-1")
SECRET_NAME = os.getenv("AUTH_SECRET_NAME", "lx-fta-auth-secrets")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")


def get_boto3_session():
    """Create a boto3 session with optional env credentials (fallback to IAM role)."""
    if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
        logger.info("Using AWS credentials from environment variables.")
        return boto3.Session(
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=REGION
        )
    logger.info("Using IAM role or default AWS credentials.")
    return boto3.Session(region_name=REGION)


@lru_cache()
def fetch_auth_secrets():
    """Retrieve user credentials and JWT secret from AWS Secrets Manager."""
    try:
        session = get_boto3_session()
        client = session.client("secretsmanager")
        response = client.get_secret_value(SecretId=SECRET_NAME)
        secret_string = response.get("SecretString")
        if not secret_string:
            raise ValueError("Secrets Manager returned an empty string.")
        logger.info("Secrets fetched successfully from AWS Secrets Manager.")
        return json.loads(secret_string)
    except Exception as e:
        logger.error(f"Error fetching secrets: {e}")
        raise RuntimeError(f"Unable to load secrets from Secrets Manager: {e}")


class LoginRequest(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


def create_access_token(data: dict, expires_delta: timedelta = None):
    secrets = fetch_auth_secrets()
    secret_key = secrets.get("jwt_secret")
    if not secret_key:
        raise RuntimeError("JWT secret is missing in secrets.")
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, secret_key, algorithm=ALGORITHM)


async def verify_token(token: str):
    secrets = fetch_auth_secrets()
    secret_key = secrets.get("jwt_secret")
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
    secrets = fetch_auth_secrets()
    user = secrets.get(req.username)
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
    secrets = fetch_auth_secrets()
    secret_key = secrets.get("jwt_secret")
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
    try:
        secrets = fetch_auth_secrets()
        if "jwt_secret" not in secrets:
            raise HTTPException(status_code=500, detail="JWT secret not found in Secrets Manager.")
        return {"status": "ok", "message": "Secrets are accessible."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Secrets access error: {e}")
