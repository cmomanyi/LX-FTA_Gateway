import traceback
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from app.auth.auth import router as auth_router
from app.sensors.generic_sensors import router as generic_sensors_router
from app.simulate_attacks.sensor_simulation_attack import router as simulate_attacks_router
from app.sensors.generic_threats_simulator import router as generic_threats_simulator_router

app = FastAPI(title="LX-FTA_Gateway API")

# ✅ Enable CORS for frontend domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://portal.lx-gateway.tech","http://localhost:3000","http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Register routers
app.include_router(auth_router)
app.include_router(generic_sensors_router)
app.include_router(simulate_attacks_router)
app.include_router(generic_threats_simulator_router)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
def root():
    return {"message": "API is live"}


@app.options("/login")
def handle_options():
    return {"message": "OPTIONS received"}


# ✅ Unified middleware for logging and error catching
@app.middleware("http")
async def unified_middleware(request: Request, call_next):
    print(f"📥 {request.method} {request.url} — headers: {dict(request.headers)}")
    try:
        response = await call_next(request)
        print(f"🔁 {request.method} {request.url} → {response.status_code}")
        return response
    except Exception as e:
        print(f"🚨 Unhandled Exception: {e}")
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal Server Error"}
        )
