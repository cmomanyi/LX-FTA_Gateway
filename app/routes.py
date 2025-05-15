from datetime import datetime

from fastapi import FastAPI, Request
import random
from app.basic_sensor_model import SoilData, AtmosphericData, WaterData, ThreatData, PlantData
from auth.auth import router as auth_router
from fastapi.middleware.cors import CORSMiddleware
from app.websocket_routes import router as websocket_router
from app.firmware_simulation import router as firmware_router
from app.attack_simulation_dashboard import router as dashboard_router
from app.shap_model import router as shap_model

app = FastAPI(title="Secure Gateway API")
# CORS settings for frontend (e.g. React dev server)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register authentication routes
app.include_router(auth_router)
app.include_router(websocket_router)

app.include_router(firmware_router)

app.include_router(dashboard_router)

# app.include_router(shap_model)

anomaly_logs = []

sensor_status = {
    "soil": ["active", "sleeping", "compromised"],
    "atmosphere": ["active", "sleeping", "compromised"],
    "water": ["active", "sleeping", "compromised"],
    "threat": ["active", "compromised", "alerting"],
    "plant": ["healthy", "wilting", "diseased"]
}

# Simulated in-memory audit log (replace with DB in production)
# audit_logs = [
#     {
#         "time": datetime.utcnow().isoformat(),
#         "sensor": "soil-001",
#         "type": "spoofing",
#         "status": "blocked"
#     },
#     {
#         "time": datetime.utcnow().isoformat(),
#         "sensor": "water-002",
#         "type": "replay",
#         "status": "secure"
#     }
# ]
SENSOR_ATTACKS = {
    "soil": ["spoofing", "replay", "firmware_injection"],
    "water": ["overflow", "salinity_spike", "signal_jam"],
    "plant": ["growth_tamper", "leaf_spot_injection", "biomass_overload"],
    "atmospheric": ["sensor_drift", "wind_spike_injection", "humidity_desync"],
    "threat": ["unauthorized_access", "jamming", "anomaly_score_spike", "radiation_leak"]
}

@app.get("/api/soil", response_model=list[SoilData])
def get_soil_data():
    return [
        SoilData(
            sensor_id=f"soil-{1000 + i}",
            temperature=round(random.uniform(15.0, 35.0), 2),
            moisture=round(random.uniform(20.0, 80.0), 2),
            ph=round(random.uniform(5.5, 7.5), 2),
            nutrient_level=round(random.uniform(1.0, 5.0), 2),
            battery_level=round(random.uniform(10.0, 100.0), 2),
            status=random.choice(sensor_status["soil"])
        )
        for i in range(5)
    ]


@app.get("/api/atmosphere", response_model=list[AtmosphericData])
def get_atmospheric_data():
    return [
        AtmosphericData(
            sensor_id=f"atmo-{1000 + i}",
            air_temperature=round(random.uniform(10.0, 40.0), 2),
            humidity=round(random.uniform(30.0, 90.0), 2),
            co2=round(random.uniform(300.0, 600.0), 2),
            wind_speed=round(random.uniform(0.0, 20.0), 2),
            rainfall=round(random.uniform(0.0, 50.0), 2),
            battery_level=round(random.uniform(10.0, 100.0), 2),
            status=random.choice(sensor_status["atmosphere"])
        )
        for i in range(5)
    ]


@app.get("/api/water", response_model=list[WaterData])
def get_water_data():
    return [
        WaterData(
            sensor_id=f"water-{1000 + i}",
            flow_rate=round(random.uniform(0.5, 5.0), 2),
            water_level=round(random.uniform(0.1, 10.0), 2),
            salinity=round(random.uniform(0.0, 35.0), 2),
            ph=round(random.uniform(6.5, 8.5), 2),
            turbidity=round(random.uniform(0.0, 100.0), 2),
            battery_level=round(random.uniform(10.0, 100.0), 2),
            status=random.choice(sensor_status["water"])
        )
        for i in range(5)
    ]


@app.get("/api/threat", response_model=list[ThreatData])
def get_threat_data():
    return [
        ThreatData(
            sensor_id=f"threat-{1000 + i}",
            unauthorized_access=random.randint(0, 3),
            jamming_signal=random.randint(0, 2),
            tampering_attempts=random.randint(0, 5),
            spoofing_attempts=random.randint(0, 4),
            anomaly_score=round(random.uniform(0.0, 1.0), 2),
            battery_level=round(random.uniform(10.0, 100.0), 2),
            status=random.choice(sensor_status["threat"])
        )
        for i in range(5)
    ]


@app.get("/api/plant", response_model=list[PlantData])
def get_plant_data():
    return [
        PlantData(
            sensor_id=f"plant-{1000 + i}",
            leaf_moisture=round(random.uniform(30.0, 80.0), 2),
            chlorophyll_level=round(random.uniform(20.0, 70.0), 2),
            growth_rate=round(random.uniform(0.5, 2.0), 2),
            disease_risk=round(random.uniform(0.0, 1.0), 2),
            stem_diameter=round(random.uniform(0.2, 2.0), 2),
            battery_level=round(random.uniform(10.0, 100.0), 2),
            status=random.choice(sensor_status["plant"])
        )
        for i in range(5)
    ]


@app.post("/log/anomaly")
async def log_anomaly(request: Request):
    anomaly = await request.json()
    anomaly_logs.append(anomaly)
    print("Anomaly logged:", anomaly)
    return {"status": "logged"}


@app.get("/log/anomalies")
def get_anomalies():
    return anomaly_logs  # Replace with file/db load if needed

def generate_fake_log(sensor_type: str, sensor_num: int):
    return {
        "time": datetime.utcnow().isoformat(),
        "sensor": f"{sensor_type}-{str(sensor_num).zfill(3)}",
        "type": random.choice(SENSOR_ATTACKS[sensor_type]),
        "status": random.choice(["secure", "blocked"])
    }

@app.get("/api/audit")
async def get_audit_logs():
    logs = []
    for sensor_type in SENSOR_ATTACKS:
        for i in range(1, 4):  # 3 logs per type
            logs.append(generate_fake_log(sensor_type, i))
    return logs
@app.get("/")
def read_root():
    return {"message": "✅ Secure Gateway API is running."}
