#
from datetime import datetime

import boto3
from fastapi import APIRouter, HTTPException
import random
import asyncio
from statistics import mean
import logging

from starlette.responses import JSONResponse

from app.simulate_attacks.attack_log import get_attack_logs
from app.simulate_attacks.sensor_simulation_attack import cache_sensor_ids, _alerts_cache
from app.utils.dynamodb_helper import put_item
from app.model.basic_sensor_model import (
    SoilData, AtmosphericData, WaterData, ThreatData, PlantData
)
from app.cache.sensor_cache import sensor_id_cache, latest_data_cache
from statistics import mean, StatisticsError


sensor_router = APIRouter()
anomaly_logs = []
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DYNAMODB_TABLE = "lx-fta-audit-logs"
dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
table = dynamodb.Table(DYNAMODB_TABLE)

TABLE_MAP = {
    "soil": "lx-fta-soil-data",
    "atmospheric": "lx-fta-atmospheric-data",
    "water": "lx-fta-water-data",
    "plant": "lx-fta-plant-data",
    "threat": "lx-fta-threat-data"
}

sensor_status = {
    "soil": ["active", "sleeping", "compromised"],
    "atmospheric": ["active", "sleeping", "compromised"],
    "water": ["active", "sleeping", "compromised"],
    "threat": ["active", "compromised", "alerting"],
    "plant": ["healthy", "wilting", "diseased"]
}

ALIASES = {
    "atmospheric": "atmospheric",
    "atm": "atmospheric"
}


# Sensor Generators

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
        status=random.choice(sensor_status["atmospheric"]),
        updated_at=datetime.utcnow().isoformat()
    )
    put_item(TABLE_MAP["atmospheric"], item.dict())
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


# Cache Refresher

def update_sensor_id_cache():
    sensor_id_cache.clear()
    for sensor_list in latest_data_cache.values():
        for sensor in sensor_list:
            sensor_id_cache.add(sensor.sensor_id)


async def refresh_sensor_data():
    while True:
        latest_data_cache["soil"] = [generate_soil_sensor(i) for i in range(5)]
        latest_data_cache["atmospheric"] = [generate_atmospheric_sensor(i) for i in range(5)]
        latest_data_cache["water"] = [generate_water_sensor(i) for i in range(5)]
        latest_data_cache["plant"] = [generate_plant_sensor(i) for i in range(5)]
        latest_data_cache["threat"] = [generate_threat_sensor(i) for i in range(5)]
        update_sensor_id_cache()
        await asyncio.sleep(5)


@sensor_router.on_event("startup")
async def startup_event():
    asyncio.create_task(refresh_sensor_data())


@sensor_router.get("/api/type_senser")
async def get_sensor_types():
    await cache_sensor_ids()
    return {
        "sensor_types": ["soil", "water", "plant", "atmospheric", "threat"],
        "sensor_ids": list(sensor_id_cache)
    }


@sensor_router.get("/api/sensor-ids")
def list_sensor_ids():
    return {"sensor_ids": list(sensor_id_cache)}


@sensor_router.get("/api/attack-types")
def get_attack_types():
    try:
        logger.info("Returning available attack types")
        return {
            "attack_types": [
                {"type": "spoofing", "description": "Simulates ECC signature mismatch",
                 "sample": {"sensor_id": "sensor-x", "payload": "abc123", "ecc_signature": "invalid_hash"}},
                {"type": "replay", "description": "Sends repeated nonce/timestamp values",
                 "sample": {"sensor_id": "sensor-x", "timestamp": datetime.utcnow().isoformat(),
                            "nonce": "nonce-123456"}},
                {"type": "firmware", "description": "Attempts to upload invalid firmware signature",
                 "sample": {"sensor_id": "sensor-x", "firmware_version": "1.0.3",
                            "firmware_signature": "invalid_signature"}},
                {"type": "ml_evasion", "description": "Triggers a drift detection anomaly",
                 "sample": {"sensor_id": "sensor-x", "values": [1.2, 2.3, 3.4]}},
                {"type": "ddos", "description": "Sends many requests in a short timeframe",
                 "sample": {"sensor_id": "sensor-x", "threshold": 10}},
                {"type": "sensor_hijack", "description": "Simulates a hijacked sensor stream",
                 "sample": {"sensor_id": "sensor-x"}},
                {"type": "api_abuse", "description": "Simulates abuse of open API endpoints",
                 "sample": {"sensor_id": "sensor-x"}},
                {"type": "tamper_breach", "description": "Simulates unauthorized tampering",
                 "sample": {"sensor_id": "sensor-x"}},
                {"type": "side_channel", "description": "Simulates side-channel data leakage",
                 "sample": {"sensor_id": "sensor-x"}}
            ]
        }
    except Exception as e:
        logger.exception("Failed to get attack types")
        raise HTTPException(status_code=500, detail="Failed to retrieve attack types")





@sensor_router.get("/api/averages")
def get_sensor_averages():
    def compute_averages(data: list[dict], fields: list[str]):
        averages = {}
        for field in fields:
            try:
                values = [d.get(field) for d in data if isinstance(d.get(field), (int, float))]
                if not values:
                    averages[field] = None
                else:
                    averages[field] = round(mean(values), 2)
            except StatisticsError:
                averages[field] = None
            except Exception as e:
                print(f"⚠️ Error computing field '{field}':", e)
                averages[field] = None
        return averages

    try:
        return {
            "soil": compute_averages([d.dict() for d in latest_data_cache.get("soil", [])],
                                     ["temperature", "moisture", "ph", "nutrient_level"]),
            "atmospheric": compute_averages([d.dict() for d in latest_data_cache.get("atmospheric", [])],
                                            ["air_temperature", "humidity", "co2", "wind_speed", "rainfall"]),
            "water": compute_averages([d.dict() for d in latest_data_cache.get("water", [])],
                                      ["flow_rate", "water_level", "salinity", "ph", "turbidity"]),
            "plant": compute_averages([d.dict() for d in latest_data_cache.get("plant", [])],
                                      ["leaf_moisture", "chlorophyll_level", "growth_rate", "disease_risk",
                                       "stem_diameter"]),
            "threat": compute_averages([d.dict() for d in latest_data_cache.get("threat", [])],
                                       ["unauthorized_access", "jamming_signal", "tampering_attempts",
                                        "spoofing_attempts", "anomaly_score"])
        }
    except Exception as e:
        print("❌ Failed to compute sensor averages:", e)
        raise HTTPException(status_code=500, detail="Failed to compute sensor averages")


@sensor_router.get("/api/logs")
def fetch_logs():
    try:
        return {"logs": get_attack_logs()}
    except Exception as e:
        logger.exception("Failed to fetch logs")
        raise HTTPException(status_code=500, detail="Error fetching logs")


@sensor_router.get("/api/alerts")
def get_latest_alerts():
    try:
        if not _alerts_cache:
            for _ in range(3):
                _alerts_cache.append({
                    "timestamp": datetime.utcnow().isoformat(),
                    "sensor_id": "sensor-x",
                    "message": "Simulated live alert",
                    "level": "info"
                })
        return JSONResponse(content={"alerts": _alerts_cache[-10:]})
    except Exception as e:
        logger.exception("Failed to get alerts")
        raise HTTPException(status_code=500, detail="Error fetching alerts")


@sensor_router.get("/api/{sensor_type}")
def get_sensor_data(sensor_type: str):
    sensor_type = ALIASES.get(sensor_type, sensor_type)
    print(f"sensor type are {sensor_type}")
    if sensor_type not in latest_data_cache:
        raise HTTPException(status_code=404, detail=f"Sensor type '{sensor_type}' not found.")
    return latest_data_cache[sensor_type]


# Validation Function

def validate_sensor_id(sensor_id: str):
    if sensor_id not in sensor_id_cache:
        raise HTTPException(status_code=400, detail="Invalid sensor ID")
    return True


@sensor_router.delete("/api/logs", tags=["Logs"])
def delete_all_logs():
    try:
        # Scan all items (NOTE: expensive for large tables)
        response = table.scan()
        items = response.get("Items", [])

        with table.batch_writer() as batch:
            for item in items:
                batch.delete_item(
                    Key={
                        "id": item["id"],
                        "timestamp": item["timestamp"]
                    }
                )
        return {"message": f"{len(items)} logs deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
