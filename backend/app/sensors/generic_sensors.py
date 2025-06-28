from datetime import datetime
from fastapi import APIRouter, Request, HTTPException
import random
import asyncio
from typing import List
from statistics import mean
from app.utils.dynamodb_helper import put_item
from app.model.basic_sensor_model import (
    SoilData, AtmosphericData, WaterData, ThreatData, PlantData
)

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

ALIASES = {
    "atmospheric": "atmosphere"
}

latest_data_cache = {
    "soil": [],
    "atmosphere": [],
    "water": [],
    "threat": [],
    "plant": []
}


# Sensor Data Generators

def generate_soil_sensor(index: int) -> SoilData:
    item = SoilData(
        sensor_id=f"soil-{1000 + index}",
        temperature=round(random.uniform(15, 30), 2),
        moisture=round(random.uniform(20, 70), 2),
        ph=round(random.uniform(5.0, 7.5), 2),
        nutrient_level=round(random.uniform(1.0, 5.0), 2),
        battery_level=round(random.uniform(20, 100), 2),
        status=random.choice(sensor_status["soil"]),
        updated_at=datetime.utcnow().isoformat()
    )
    put_item(TABLE_MAP["soil"], item.dict())
    return item


def generate_atmospheric_sensor(index: int) -> AtmosphericData:
    item = AtmosphericData(
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
    put_item(TABLE_MAP["atmosphere"], item.dict())
    return item


def generate_water_sensor(index: int) -> WaterData:
    item = WaterData(
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
    put_item(TABLE_MAP["water"], item.dict())
    return item


def generate_plant_sensor(index: int) -> PlantData:
    item = PlantData(
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
    put_item(TABLE_MAP["plant"], item.dict())
    return item


def generate_threat_sensor(index: int) -> ThreatData:
    item = ThreatData(
        sensor_id=f"threat-{5000 + index}",
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


# Refresher

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


# Unified Sensor Data Route
# ✅ GET /api/averages must come BEFORE the generic /api/{sensor_type} route
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


# 👇 Generic sensor fetch goes after
# @sensor_router.get("/api/{sensor_type}")
# def get_sensor_data(sensor_type: str):
#     sensor_type = ALIASES.get(sensor_type, sensor_type)
#     if sensor_type not in latest_data_cache:
#         raise HTTPException(status_code=404, detail=f"Sensor type '{sensor_type}' not found.")
#     print(f"🔍 Accessed sensor type: {sensor_type} at {datetime.utcnow().isoformat()}")
#     return latest_data_cache[sensor_type]

@sensor_router.get("/api/sensor-types")
def list_sensor_types():
    return {
        "sensor_types": list(latest_data_cache.keys()),
        "aliases": ALIASES
    }


