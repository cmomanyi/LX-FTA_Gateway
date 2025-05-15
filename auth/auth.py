from fastapi import APIRouter, HTTPException, Depends, WebSocketException, status
from pydantic import BaseModel
from datetime import datetime, timedelta
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

router = APIRouter()
SECRET_KEY = "super_secure_quantum_key"
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 60

# Simulated user database
fake_users = {
    "admin": {"password": "admin123", "role": "admin"},
    "analyst": {"password": "analyst123", "role": "analyst"},
    "sensor": {"password": "sensor123", "role": "sensor"},
}


class LoginRequest(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


security = HTTPBearer()


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# async def verify_token(token: str):
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username = payload.get("sub")
#         if username is None:
#             raise ValueError("Invalid token payload")
#         return username
#     except JWTError:
#         raise ValueError("Invalid token")

async def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
        return username
    except JWTError as e:
        print("JWT verification failed:", str(e))
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)

@router.post("/login", response_model=Token)
def login(req: LoginRequest):
    user = fake_users.get(req.username)
    if not user or user["password"] != req.password:
        raise HTTPException(status_code=401, detail="Invalid username or password.")
    token = create_access_token({"sub": req.username, "role": user["role"]}, timedelta(minutes=TOKEN_EXPIRE_MINUTES))
    return {"access_token": token, "token_type": "bearer"}


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return {"username": payload.get("sub"), "role": payload.get("role")}
    except JWTError:
        raise HTTPException(status_code=403, detail="Invalid token.")


def require_role(role: str):
    def role_checker(user=Depends(get_current_user)):
        if user["role"] != role:
            raise HTTPException(status_code=403, detail="Access forbidden.")
        return user

    return role_checker


@router.get("/protected")
def protected_route(user: dict = Depends(get_current_user)):
    return user
