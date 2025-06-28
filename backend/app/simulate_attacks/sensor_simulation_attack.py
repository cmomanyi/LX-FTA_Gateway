from datetime import datetime
from fastapi import APIRouter, Request, HTTPException
import random
import asyncio
from typing import List
from statistics import mean

from app.simulate_attacks.attack_log import get_attack_logs
from app.utils.dynamodb_helper import put_item
from app.model.basic_sensor_model import (
    SoilData, AtmosphericData, WaterData, ThreatData, PlantData
)

from datetime import datetime
import random
from app.cache.sensor_cache import sensor_id_cache, latest_data_cache
from app.utils.dynamodb_helper import put_alert_to_audit_log
from starlette.responses import JSONResponse

router = APIRouter()
anomaly_logs = []
# ✅ Define this near the top
_alerts_cache = []

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
    "atmosphere": "atmospheric"
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

def update_sensor_id_cache():
    global sensor_id_cache
    sensor_id_cache = {sensor.sensor_id for sensors in latest_data_cache.values() for sensor in sensors}


async def refresh_sensor_data():
    while True:
        latest_data_cache["soil"] = [generate_soil_sensor(i) for i in range(5)]
        latest_data_cache["atmosphere"] = [generate_atmospheric_sensor(i) for i in range(5)]
        latest_data_cache["water"] = [generate_water_sensor(i) for i in range(5)]
        latest_data_cache["plant"] = [generate_plant_sensor(i) for i in range(5)]
        latest_data_cache["threat"] = [generate_threat_sensor(i) for i in range(5)]
        update_sensor_id_cache()
        await asyncio.sleep(5)


@router.on_event("startup")
async def startup_event():
    asyncio.create_task(refresh_sensor_data())


# List Sensor Types

@router.get("/api/sensor-types")
def list_sensor_types():
    return {
        "sensor_types": list(latest_data_cache.keys()),
        "aliases": ALIASES,
        "sensor_ids": list(sensor_id_cache)
    }


# Unified Sensor Data Route

# @router.get("/api/{sensor_type}")
# def get_sensor_data(sensor_type: str):
#     sensor_type = ALIASES.get(sensor_type, sensor_type)
#     if sensor_type not in latest_data_cache:
#         raise HTTPException(status_code=404, detail=f"Sensor type '{sensor_type}' not found.")
#     print(f"🔍 Accessed sensor type: {sensor_type} at {datetime.utcnow().isoformat()}")
#     return latest_data_cache[sensor_type]


@router.get("/api/averages")
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


@router.get("/api/logs")
def fetch_logs():
    return {"logs": get_attack_logs()}


#
# @router.get("/api/alerts")
# def get_latest_alerts(
#         limit: int = Query(default=10, ge=1, le=100),
#         level: str = Query(default=None, description="Filter alerts by level (e.g., info, warning, critical)"),
#         sensor_id: str = Query(default=None, description="Filter by specific sensor_id")
# ):
#     """
#     Returns the latest sensor alerts. Supports optional filtering by sensor ID and alert level.
#     If cache is empty, simulates 3 sample alerts using random sensor IDs.
#     """
#
#     # Populate dummy alerts if cache is empty
#     if not _alerts_cache:
#         for _ in range(3):
#             _alerts_cache.append({
#                 "timestamp": datetime.utcnow().isoformat(),
#                 "sensor_id": random.choice(list(sensor_id_cache)) if sensor_id_cache else "sensor-x",
#                 "message": "Simulated live alert",
#                 "level": random.choice(["info", "warning", "critical"])
#             })
#
#     # Work on a copy to avoid thread/race issues
#     filtered_alerts = list(_alerts_cache)
#
#     # Optional filtering
#     if level:
#         filtered_alerts = [a for a in filtered_alerts if a["level"] == level]
#     if sensor_id:
#         filtered_alerts = [a for a in filtered_alerts if a["sensor_id"] == sensor_id]
#
#     return JSONResponse(
#         status_code=200,
#         content={"alerts": filtered_alerts[-limit:]}
#     )

@router.get("/api/alerts")
def get_latest_alerts():
    if not _alerts_cache:
        for _ in range(3):
            alert = {
                "timestamp": datetime.utcnow().isoformat(),
                "sensor_id": random.choice(list(sensor_id_cache)) if sensor_id_cache else "sensor-x",
                "message": "Simulated live alert",
                "level": random.choice(["info", "warning", "critical"])
            }
            _alerts_cache.append(alert)
            put_alert_to_audit_log(alert)  # 🔁 Persist to DynamoDB audit logs

    return JSONResponse(content={"alerts": _alerts_cache[-10:]})


def get_all_sensor_ids():
    return list(sensor_id_cache)


def validate_sensor_id(sensor_id: str):
    if sensor_id not in sensor_id_cache:
        raise HTTPException(status_code=400, detail="Invalid sensor ID")
    return True
