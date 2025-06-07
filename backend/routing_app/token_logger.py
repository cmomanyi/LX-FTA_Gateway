from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from jose import jwt, JWTError
from auth.auth import SECRET_KEY, ALGORITHM

class TokenLoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        token = request.headers.get("Authorization")

        if token and token.startswith("Bearer "):
            try:
                jwt.decode(token.split(" ")[1], SECRET_KEY, algorithms=[ALGORITHM])
            except JWTError as e:
                print(f"[TOKEN REJECTED] {request.url.path} - {str(e)}")
        elif "api" in str(request.url):
            print(f"[NO TOKEN] {request.url.path} - Missing or malformed Authorization")

        response = await call_next(request)
        return response
