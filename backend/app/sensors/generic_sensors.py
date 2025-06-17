from datetime import datetime

import numpy as np
from fastapi import HTTPException, Request, APIRouter


import random

from backend.app.model.basic_sensor_model import SoilData, AtmosphericData, WaterData, ThreatData, PlantData

router = APIRouter()

np.random.seed(42)

anomaly_logs = []

sensor_status = {
    "soil": ["active", "sleeping", "compromised"],
    "atmosphere": ["active", "sleeping", "compromised"],
    "water": ["active", "sleeping", "compromised"],
    "threat": ["active", "compromised", "alerting"],
    "plant": ["healthy", "wilting", "diseased"]
}


# ]
SENSOR_ATTACKS = {
    "soil": ["spoofing", "replay", "firmware_injection"],
    "water": ["overflow", "salinity_spike", "signal_jam"],
    "plant": ["growth_tamper", "leaf_spot_injection", "biomass_overload"],
    "atmospheric": ["sensor_drift", "wind_spike_injection", "humidity_desync"],
    "threat": ["unauthorized_access", "jamming", "anomaly_score_spike", "radiation_leak"]
}


@router.get("/api/soil", response_model=list[SoilData])
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


@router.get("/api/atmosphere", response_model=list[AtmosphericData])
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


@router.get("/api/water", response_model=list[WaterData])
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


@router.get("/api/threat", response_model=list[ThreatData])
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


@router.get("/api/plant", response_model=list[PlantData])
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


@router.post("/log/anomaly")
async def log_anomaly(request: Request):
    anomaly = await request.json()
    anomaly_logs.append(anomaly)
    print("Anomaly logged:", anomaly)
    return {"status": "logged"}


@router.get("/log/anomalies")
def get_anomalies():
    return anomaly_logs  # Replace with file/db load if needed


def generate_fake_log(sensor_type: str, sensor_num: int):
    return {
        "time": datetime.utcnow().isoformat(),
        "sensor": f"{sensor_type}-{str(sensor_num).zfill(3)}",
        "type": random.choice(SENSOR_ATTACKS[sensor_type]),
        "status": random.choice(["secure", "blocked"])
    }


@router.get("/api/audit")
async def get_audit_logs():
    logs = []
    for sensor_type in SENSOR_ATTACKS:
        for i in range(1, 4):  # 3 logs per type
            logs.append(generate_fake_log(sensor_type, i))
    return logs


