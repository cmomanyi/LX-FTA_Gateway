from pydantic import BaseModel


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
