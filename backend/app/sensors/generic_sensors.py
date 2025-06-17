# app/routes/sensor_router.py

from fastapi import APIRouter
from app.utils.dynamodb_helper import get_all_items
from app.model.basic_sensor_model import (
    SoilData, AtmosphericData, WaterData, ThreatData, PlantData
)

router = APIRouter()

@router.get("/api/soil", response_model=list[SoilData])
def get_soil_data():
    return get_all_items(SoilData, "soil")

@router.get("/api/atmosphere", response_model=list[AtmosphericData])
def get_atmospheric_data():
    return get_all_items(AtmosphericData, "atmospheric")

@router.get("/api/water", response_model=list[WaterData])
def get_water_data():
    return get_all_items(WaterData, "water")

@router.get("/api/threat", response_model=list[ThreatData])
def get_threat_data():
    return get_all_items(ThreatData, "threat")

@router.get("/api/plant", response_model=list[PlantData])
def get_plant_data():
    return get_all_items(PlantData, "plant")
