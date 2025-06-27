from datetime import datetime
from fastapi import APIRouter, Request
import random
import asyncio

from app.model.basic_sensor_model import SoilData, AtmosphericData, WaterData, ThreatData, PlantData
from app.utils.dynamodb_helper import get_all_items
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


async def refresh_sensor_data():
    while True:
        for sensor_type, model, table in [
            ("soil", SoilData, "soil"),
            ("atmosphere", AtmosphericData, "atmospheric"),
            ("water", WaterData, "water"),
            ("threat", ThreatData, "threat"),
            ("plant", PlantData, "plant")
        ]:
            fetched = get_all_items(model, table)
            randomized = []
            for item in fetched:
                item_dict = item.dict()
                for key, val in item_dict.items():
                    if isinstance(val, (int, float)):
                        item_dict[key] = round(val * random.uniform(0.9, 1.1), 2)
                item_dict["status"] = random.choice(sensor_status[sensor_type])
                randomized.append(model(**item_dict))
            latest_data_cache[sensor_type] = randomized
        await asyncio.sleep(5)


@sensor_router.on_event("startup")
async def startup_event():
    asyncio.create_task(refresh_sensor_data())


@sensor_router.get("/api/soil", response_model=list[SoilData])
def get_soil_data():
    return latest_data_cache["soil"]


@sensor_router.get("/api/atmosphere", response_model=list[AtmosphericData])
def get_atmospheric_data():
    return latest_data_cache["atmosphere"]


@sensor_router.get("/api/water", response_model=list[WaterData])
def get_water_data():
    return latest_data_cache["water"]


@sensor_router.get("/api/threat", response_model=list[ThreatData])
def get_threat_data():
    return latest_data_cache["threat"]


@sensor_router.get("/api/plant", response_model=list[PlantData])
def get_plant_data():
    return latest_data_cache["plant"]


@sensor_router.post("/log/anomaly")
async def log_anomaly(request: Request):
    anomaly = await request.json()
    anomaly_logs.append(anomaly)
    print("Anomaly logged:", anomaly)
    return {"status": "logged"}


@sensor_router.get("/log/anomalies")
def get_anomalies():
    return anomaly_logs


def generate_fake_log(sensor_type: str, sensor_num: int):
    return {
        "time": datetime.utcnow().isoformat(),
        "sensor": f"{sensor_type}-{str(sensor_num).zfill(3)}",
        "type": random.choice(SENSOR_ATTACKS[sensor_type]),
        "status": random.choice(["secure", "blocked"])
    }


@sensor_router.get("/api/audit")
async def get_audit_logs():
    logs = []
    for sensor_type in SENSOR_ATTACKS:
        for i in range(1, 4):
            logs.append(generate_fake_log(sensor_type, i))
    return logs

def compute_averages(data: list[dict], fields: list[str]):
    return {field: round(mean([d[field] for d in data if isinstance(d[field], (int, float))]), 2) for field in fields}

@sensor_router.get("/api/averages")
async def get_sensor_averages():
    return {
        "soil": compute_averages([d.dict() for d in get_all_items(SoilData, "soil")],
                                 ["temperature", "moisture", "ph", "nutrient_level"]),
        "atmosphere": compute_averages([d.dict() for d in get_all_items(AtmosphericData, "atmospheric")],
                                       ["air_temperature", "humidity", "co2", "wind_speed", "rainfall"]),
        "water": compute_averages([d.dict() for d in get_all_items(WaterData, "water")],
                                  ["flow_rate", "water_level", "salinity", "ph", "turbidity"]),
        "plant": compute_averages([d.dict() for d in get_all_items(PlantData, "plant")],
                                  ["leaf_moisture", "chlorophyll_level", "growth_rate", "disease_risk", "stem_diameter"]),
        "threat": compute_averages([d.dict() for d in get_all_items(ThreatData, "threat")],
                                   ["unauthorized_access", "jamming_signal", "tampering_attempts", "spoofing_attempts", "anomaly_score"])
    }
# @sensor_router.get("/")
# def read_root():
#     return {"message": "✅ Secure Gateway API is running."}


# @sensor_router.get("/health")
# def health():
#     return {"status": "ok"}
