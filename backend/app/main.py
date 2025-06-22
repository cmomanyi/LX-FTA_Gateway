import traceback

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request, WebSocket
from starlette.responses import JSONResponse, Response

from app.auth.auth import router as auth_router
from app.sensors.generic_sensors import router as generic_sensors_router
from app.simulate_attacks.sensor_simulation_attack import router as simulate_attacks_router
from app.sensors.generic_threats_simulator import router as generic_threats_simulator_router
from datetime import datetime
import asyncio
import random

app = FastAPI(title="LX-FTA_Gateway API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://portal.lx-gateway.tech"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes AFTER middleware
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


@app.get("/")
def root():
    return {"message": "API is live"}


@app.options("/login")
def preflight_login():
    response = Response()
    response.headers["Access-Control-Allow-Origin"] = "https://portal.lx-gateway.tech"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    return response


@app.websocket("/ws/alerts")
async def websocket_alerts(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Simulate dummy alert data
            alert = {
                "timestamp": datetime.utcnow().isoformat(),
                "sensor_id": random.choice([
                    "soil-1000", "water-1001", "threat-1002", "plant-1003", "atmo-1004"
                ]),
                "attack_type": random.choice([
                    "spoofing", "replay", "ddos", "drift", "firmware_injection"
                ]),
                "message": "Simulated threat activity detected.",
                "severity": random.choice(["Low", "Medium", "High"]),
                "blocked": random.choice([True, False])
            }
            await websocket.send_json(alert)
            await asyncio.sleep(5)  # Send every 5 seconds
    except Exception as e:
        print(f"⚠️ WebSocket connection closed: {e}")
