import traceback

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request,WebSocket
from starlette.responses import JSONResponse

from app.auth.auth import router as auth_router
from app.sensors.generic_sensors import router as generic_sensors_router
from app.simulate_attacks.sensor_simulation_attack import router as simulate_attacks_router
from app.sensors.generic_threats_simulator import router as generic_threats_simulator_router

app = FastAPI(title="LX-FTA_Gateway API")
# "http://localhost:3000"
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://portal.lx-gateway.tech"],  # ✅ EXACT origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Register routes AFTER middleware
app.include_router(auth_router)
app.include_router(generic_sensors_router)

app.include_router(simulate_attacks_router)

app.include_router(generic_threats_simulator_router)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.middleware("http")
async def log_requests(request, call_next):
    print(f"📥 {request.method} {request.url} — headers: {dict(request.headers)}")
    response = await call_next(request)
    print(f"🔁 {request.method} {request.url} → {response.status_code}")
    return response


app.include_router(auth_router)


@app.options("/login")
def handle_options():
    return {"message": "OPTIONS received"}


@app.get("/")
def root():
    return {"message": "API is live"}

@app.middleware("http")
async def log_exceptions(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        print(f"🚨 Unhandled Exception: {e}")
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal Server Error"}

        )


@app.websocket("/ws/alerts")
async def websocket_alerts(websocket: WebSocket):
    await websocket.accept()
    while True:
        await websocket.send_json({"timestamp": ..., "sensor_id": ..., ...})
