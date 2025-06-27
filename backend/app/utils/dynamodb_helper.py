from datetime import datetime
from fastapi import APIRouter, Request
import random
import asyncio
from typing import List
from app.model.basic_sensor_model import SoilData, AtmosphericData, WaterData, ThreatData, PlantData
from statistics import mean

sensor_router = APIRouter()

anomaly_logs = []

sensor_status = {
    "soil": ["active", "sleeping", "compromised"],
    "atmosphere": ["active", "sleeping", "compromised"],
    "water": ["active", "sleeping", "compromised"],
    "threat": ["active", "compromised", "alerting"],
    "plant": ["healthy", "wilting", "diseased"]
}

SENSOR_ATTACKS = {
    "soil": ["spoofing", "replay", "firmware_injection"],
    "water": ["overflow", "salinity_spike", "signal_jam"],
    "plant": ["growth_tamper", "leaf_spot_injection", "biomass_overload"],
    "atmospheric": ["sensor_drift", "wind_spike_injection", "humidity_desync"],
    "threat": ["unauthorized_access", "jamming", "anomaly_score_spike", "radiation_leak"]
}

latest_data_cache = {
    "soil": [],
    "atmosphere": [],
    "water": [],
    "threat": [],
    "plant": []
}


def generate_soil_sensor(index: int) -> SoilData:
    return SoilData(
        sensor_id=f"soil-{1000 + index}",
        temperature=round(random.uniform(15, 30), 2),
        moisture=round(random.uniform(20, 70), 2),
        ph=round(random.uniform(5.0, 7.5), 2),
        nutrient_level=round(random.uniform(1.0, 5.0), 2),
        battery_level=round(random.uniform(20, 100), 2),
        status=random.choice(sensor_status["soil"]),
        updated_at=datetime.utcnow().isoformat()
    )


def generate_atmospheric_sensor(index: int) -> AtmosphericData:
    return AtmosphericData(
        sensor_id=f"atm-{2000 + index}",
        air_temperature=round(random.uniform(10, 35), 2),
        humidity=round(random.uniform(30, 90), 2),
        co2=round(random.uniform(300, 700), 2),
        wind_speed=round(random.uniform(0, 15), 2),
        rainfall=round(random.uniform(0, 50), 2),
        battery_level=round(random.uniform(30, 100), 2),
        status=random.choice(sensor_status["atmosphere"]),
        updated_at=datetime.utcnow().isoformat()
    )


def generate_water_sensor(index: int) -> WaterData:
    return WaterData(
        sensor_id=f"water-{3000 + index}",
        flow_rate=round(random.uniform(1.0, 10.0), 2),
        water_level=round(random.uniform(50, 200), 2),
        salinity=round(random.uniform(0.1, 5.0), 2),
        ph=round(random.uniform(6.0, 8.0), 2),
        turbidity=round(random.uniform(1, 10), 2),
        battery_level=round(random.uniform(20, 100), 2),
        status=random.choice(sensor_status["water"]),
        updated_at=datetime.utcnow().isoformat()
    )


def generate_plant_sensor(index: int) -> PlantData:
    return PlantData(
        sensor_id=f"plant-{4000 + index}",
        leaf_moisture=round(random.uniform(30, 80), 2),
        chlorophyll_level=round(random.uniform(1.0, 5.0), 2),
        growth_rate=round(random.uniform(0.5, 3.0), 2),
        disease_risk=round(random.uniform(0.0, 1.0), 2),
        stem_diameter=round(random.uniform(0.5, 2.0), 2),
        battery_level=round(random.uniform(20, 100), 2),
        status=random.choice(sensor_status["plant"]),
        updated_at=datetime.utcnow().isoformat()
    )


def generate_threat_sensor(index: int) -> ThreatData:
    return ThreatData(
        sensor_id=f"threat-{5000 + index}",
        unauthorized_access=random.randint(0, 5),
        jamming_signal=random.randint(0, 3),
        tampering_attempts=random.randint(0, 4),
        spoofing_attempts=random.randint(0, 3),
        anomaly_score=round(random.uniform(0.0, 1.0), 2),
        status=random.choice(sensor_status["threat"]),
        updated_at=datetime.utcnow().isoformat()
    )


async def refresh_sensor_data():
    while True:
        latest_data_cache["soil"] = [generate_soil_sensor(i) for i in range(5)]
        latest_data_cache["atmosphere"] = [generate_atmospheric_sensor(i) for i in range(5)]
        latest_data_cache["water"] = [generate_water_sensor(i) for i in range(5)]
        latest_data_cache["plant"] = [generate_plant_sensor(i) for i in range(5)]
        latest_data_cache["threat"] = [generate_threat_sensor(i) for i in range(5)]
        await asyncio.sleep(5)


@sensor_router.on_event("startup")
async def startup_event():
    asyncio.create_task(refresh_sensor_data())


@sensor_router.get("/api/soil", response_model=List[SoilData])
def get_soil_data():
    return latest_data_cache["soil"]


@sensor_router.get("/api/atmosphere", response_model=List[AtmosphericData])
def get_atmospheric_data():
    return latest_data_cache["atmosphere"]


@sensor_router.get("/api/water", response_model=List[WaterData])
def get_water_data():
    return latest_data_cache["water"]


@sensor_router.get("/api/threat", response_model=List[ThreatData])
def get_threat_data():
    return latest_data_cache["threat"]


@sensor_router.get("/api/plant", response_model=List[PlantData])
def get_plant_data():
    return latest_data_cache["plant"]


@sensor_router.get("/api/averages")
def get_sensor_averages():
    def compute_averages(data: list[dict], fields: list[str]):
        return {
            field: round(mean([d[field] for d in data if isinstance(d[field], (int, float))]), 2)
            for field in fields
        }

    return {
        "soil": compute_averages([d.dict() for d in latest_data_cache["soil"]],
                                 ["temperature", "moisture", "ph", "nutrient_level"]),
        "atmosphere": compute_averages([d.dict() for d in latest_data_cache["atmosphere"]],
                                       ["air_temperature", "humidity", "co2", "wind_speed", "rainfall"]),
        "water": compute_averages([d.dict() for d in latest_data_cache["water"]],
                                  ["flow_rate", "water_level", "salinity", "ph", "turbidity"]),
        "plant": compute_averages([d.dict() for d in latest_data_cache["plant"]],
                                  ["leaf_moisture", "chlorophyll_level", "growth_rate", "disease_risk",
                                   "stem_diameter"]),
        "threat": compute_averages([d.dict() for d in latest_data_cache["threat"]],
                                   ["unauthorized_access", "jamming_signal", "tampering_attempts", "spoofing_attempts",
                                    "anomaly_score"])
    }


# Anomaly logging
@sensor_router.post("/log/anomaly")
async def log_anomaly(request: Request):
    anomaly = await request.json()
    anomaly_logs.append(anomaly)
    print("Anomaly logged:", anomaly)
    return {"status": "logged"}


@sensor_router.get("/log/anomalies")
def get_anomalies():
    return anomaly_logs


# Audit logs
@sensor_router.get("/api/audit")
def get_audit_logs():
    def generate_fake_log(sensor_type: str, sensor_num: int):
        return {
            "time": datetime.utcnow().isoformat(),
            "sensor": f"{sensor_type}-{str(sensor_num).zfill(3)}",
            "type": random.choice(SENSOR_ATTACKS[sensor_type]),
            "status": random.choice(["secure", "blocked"])
        }

    logs = []
    for sensor_type in SENSOR_ATTACKS:
        for i in range(1, 4):
            logs.append(generate_fake_log(sensor_type, i))
    return logs
