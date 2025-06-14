from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
# from aws_services.aws_services import dynamodb_put_item
from app.aws_services.aws_services import dynamodb_put_item
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.auth.auth import router as auth_router

app = FastAPI(title="LX-FTA_Gateway API")



# ✅ CORSMiddleware comes BEFORE including routers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://portal.lx-gateway.tech"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Register routes AFTER middleware
app.include_router(auth_router)

@app.get("/health")
def health():
    return {"status": "ok"}
@app.middleware("http")
async def log_requests(request, call_next):
    print(f"📥 {request.method} {request.url} — headers: {dict(request.headers)}")
    response = await call_next(request)
    print(f"🔁 {request.method} {request.url} → {response.status_code}")
    return response


# Include routes after CORS
app.include_router(auth_router)


@app.options("/login")
def handle_options():
    return {"message": "OPTIONS received"}


@app.get("/")
def root():
    return {"message": "API is live"}
#
# # ✅ CORS setup: allow only the frontend domain
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["https://portal.lx-gateway.tech"],  # Frontend domain
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
#
# # 👇 Include the authentication router
# app.include_router(auth_router)
#
# # Optional health/root check
# @app.get("/")
# def root():
#     return {"status": "ok", "message": "API is live"}
#
# app.include_router(auth_router)
#
#
# @app.post("/sensor")
# async def save_sensor_data(payload: dict):
#     try:
#         response = dynamodb_put_item(payload)
#         return {"status": "success", "response": response}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
#
#
# @app.get("/health")
# def health():
#     return {"status": "ok"}
#
# # Global exception handler for JSON validation issues
# @app.exception_handler(RequestValidationError)
# async def validation_exception_handler(request: Request, exc: RequestValidationError):
#     return JSONResponse(
#         status_code=422,
#         content={
#             "error": "Invalid request. Ensure you send a valid JSON body with required fields.",
#             "details": exc.errors(),
#         },
#     )
