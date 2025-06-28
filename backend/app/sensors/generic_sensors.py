from datetime import datetime
from fastapi import APIRouter, Request
import random
import asyncio
from typing import List
from statistics import mean
from app.utils.dynamodb_helper import put_item
from app.model.basic_sensor_model import SoilData, AtmosphericData, WaterData, ThreatData, PlantData

sensor_router = APIRouter()
anomaly_logs = []

TABLE_MAP = {
    "soil": "lx-fta-soil-data",
    "atmosphere": "lx-fta-atmospheric-data",
    "water": "lx-fta-water-data",
    "plant": "lx-fta-plant-data",
    "threat": "lx-fta-threat-data"
}

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

latest_data_cache = {key: [] for key in TABLE_MAP.keys()}


# ------------------ Sensor Generators ------------------

def generate_soil_sensor(i): return _generate_sensor(
    i, SoilData, TABLE_MAP["soil"], "soil", {
        "temperature": (15, 30), "moisture": (20, 70), "ph": (5.0, 7.5),
        "nutrient_level": (1.0, 5.0)
    })


def generate_atmospheric_sensor(i): return _generate_sensor(
    i, AtmosphericData, TABLE_MAP["atmosphere"], "atm", {
        "air_temperature": (10, 35), "humidity": (30, 90),
        "co2": (300, 700), "wind_speed": (0, 15), "rainfall": (0, 50)
    })


def generate_water_sensor(i): return _generate_sensor(
    i, WaterData, TABLE_MAP["water"], "water", {
        "flow_rate": (1.0, 10.0), "water_level": (50, 200),
        "salinity": (0.1, 5.0), "ph": (6.0, 8.0), "turbidity": (1, 10)
    })


def generate_plant_sensor(i): return _generate_sensor(
    i, PlantData, TABLE_MAP["plant"], "plant", {
        "leaf_moisture": (30, 80), "chlorophyll_level": (1.0, 5.0),
        "growth_rate": (0.5, 3.0), "disease_risk": (0.0, 1.0), "stem_diameter": (0.5, 2.0)
    })


def generate_threat_sensor(i):
    item = ThreatData(
        sensor_id=f"threat-{5000 + i}",
        unauthorized_access=random.randint(0, 5),
        jamming_signal=random.randint(0, 3),
        tampering_attempts=random.randint(0, 4),
        spoofing_attempts=random.randint(0, 3),
        anomaly_score=round(random.uniform(0.0, 1.0), 2),
        battery_level=round(random.uniform(20, 100), 2),
        status=random.choice(sensor_status["threat"]),
        updated_at=datetime.utcnow().isoformat()
    )
    put_item(TABLE_MAP["threat"], item.dict())
    return item


def _generate_sensor(i, model, table, prefix, value_ranges):
    base = {
        "sensor_id": f"{prefix}-{1000 + i}",
        "battery_level": round(random.uniform(20, 100), 2),
        "status": random.choice(sensor_status[prefix if prefix != "atm" else "atmosphere"]),
        "updated_at": datetime.utcnow().isoformat()
    }
    for field, (low, high) in value_ranges.items():
        base[field] = round(random.uniform(low, high), 2)
    item = model(**base)
    put_item(table, item.dict())
    return item


# ------------------ Refresher ------------------

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


# ------------------ API Endpoints ------------------

@sensor_router.get("/api/{sensor_type}", response_model=List)
def get_sensor_data(sensor_type: str):
    return latest_data_cache[sensor_type]


@sensor_router.get("/api/averages")
def get_sensor_averages():
    def avg(data: list, fields: list[str]):
        return {
            field: round(mean([d[field] for d in data if isinstance(d[field], (int, float))]), 2)
            for field in fields
        }

    return {
        "soil": avg([d.dict() for d in latest_data_cache["soil"]], ["temperature", "moisture", "ph", "nutrient_level"]),
        "atmosphere": avg([d.dict() for d in latest_data_cache["atmosphere"]],
                          ["air_temperature", "humidity", "co2", "wind_speed", "rainfall"]),
        "water": avg([d.dict() for d in latest_data_cache["water"]],
                     ["flow_rate", "water_level", "salinity", "ph", "turbidity"]),
        "plant": avg([d.dict() for d in latest_data_cache["plant"]],
                     ["leaf_moisture", "chlorophyll_level", "growth_rate", "disease_risk", "stem_diameter"]),
        "threat": avg([d.dict() for d in latest_data_cache["threat"]],
                      ["unauthorized_access", "jamming_signal", "tampering_attempts", "spoofing_attempts", "anomaly_score"])
    }


# ------------------ Anomaly & Audit Logging ------------------

@sensor_router.post("/log/anomaly")
async def log_anomaly(request: Request):
    data = await request.json()
    anomaly_logs.append(data)
    print("Anomaly logged:", data)
    return {"status": "logged"}


@sensor_router.get("/log/anomalies")
def get_anomalies():
    return anomaly_logs


@sensor_router.get("/api/audit")
def get_audit_logs():
    return [{
        "time": datetime.utcnow().isoformat(),
        "sensor": f"{sensor_type}-{str(i).zfill(3)}",
        "type": random.choice(SENSOR_ATTACKS[sensor_type]),
        "status": random.choice(["secure", "blocked"])
    } for sensor_type in SENSOR_ATTACKS for i in range(1, 4)]
