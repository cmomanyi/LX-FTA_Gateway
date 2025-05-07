from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from auth import router as auth_router
import random

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

# ========== Sensor Models ==========

class SoilData(BaseModel):
    sensor_id: str
    temperature: float
    moisture: float
    ph: float
    nutrient_level: float
    battery_level: float
    status: str

class AtmosphericData(BaseModel):
    sensor_id: str
    air_temperature: float
    humidity: float
    co2: float
    wind_speed: float
    rainfall: float
    battery_level: float
    status: str

class WaterData(BaseModel):
    sensor_id: str
    flow_rate: float
    water_level: float
    salinity: float
    ph: float
    turbidity: float
    battery_level: float
    status: str

class ThreatData(BaseModel):
    sensor_id: str
    unauthorized_access: int
    jamming_signal: int
    tampering_attempts: int
    spoofing_attempts: int
    anomaly_score: float
    battery_level: float
    status: str

class PlantData(BaseModel):
    sensor_id: str
    leaf_moisture: float
    chlorophyll_level: float
    growth_rate: float
    disease_risk: float
    stem_diameter: float
    battery_level: float
    status: str

# ========== Sensor Options ==========

sensor_status = {
    "soil": ["active", "sleeping", "compromised"],
    "atmosphere": ["active", "sleeping", "compromised"],
    "water": ["active", "sleeping", "compromised"],
    "threat": ["active", "compromised", "alerting"],
    "plant": ["healthy", "wilting", "diseased"]
}

# ========== Endpoints ==========

@app.get("/")
def read_root():
    return {"message": "✅ Secure Gateway API is running."}


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
