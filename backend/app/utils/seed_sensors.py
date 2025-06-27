import random
from decimal import Decimal
import boto3

from app.model.basic_sensor_model import (
    SoilData, AtmosphericData, WaterData, ThreatData, PlantData
)
from app.utils.dynamodb_helper import put_item

# Use credentials from ~/.aws/credentials under the default profile
session = boto3.Session(profile_name="default", region_name="us-east-1")
dynamodb = session.client("dynamodb")


def seed_soil_data():
    for i in range(5):
        data = SoilData(
            sensor_id=f"soil-{1000 + i}",
            temperature=round(random.uniform(15.0, 35.0), 2),
            moisture=round(random.uniform(20.0, 80.0), 2),
            ph=round(random.uniform(5.5, 7.5), 2),
            nutrient_level=round(random.uniform(1.0, 5.0), 2),
            battery_level=round(random.uniform(10.0, 100.0), 2),
            status=random.choice(["active", "sleeping", "compromised"])
        )
        put_item(data, "soil", dynamodb)


def seed_atmospheric_data():
    for i in range(5):
        data = AtmosphericData(
            sensor_id=f"atmo-{1000 + i}",
            air_temperature=round(random.uniform(10.0, 40.0), 2),
            humidity=round(random.uniform(30.0, 90.0), 2),
            co2=round(random.uniform(300.0, 600.0), 2),
            wind_speed=round(random.uniform(0.0, 20.0), 2),
            rainfall=round(random.uniform(0.0, 50.0), 2),
            battery_level=round(random.uniform(10.0, 100.0), 2),
            status=random.choice(["active", "sleeping", "compromised"])
        )
        put_item(data, "atmospheric", dynamodb)


def seed_water_data():
    for i in range(5):
        data = WaterData(
            sensor_id=f"water-{1000 + i}",
            flow_rate=round(random.uniform(0.5, 5.0), 2),
            water_level=round(random.uniform(0.1, 10.0), 2),
            salinity=round(random.uniform(0.0, 35.0), 2),
            ph=round(random.uniform(6.5, 8.5), 2),
            turbidity=round(random.uniform(0.0, 100.0), 2),
            battery_level=round(random.uniform(10.0, 100.0), 2),
            status=random.choice(["active", "sleeping", "compromised"])
        )
        put_item(data, "water", dynamodb)


def seed_threat_data():
    for i in range(5):
        data = ThreatData(
            sensor_id=f"threat-{1000 + i}",
            unauthorized_access=random.randint(0, 3),
            jamming_signal=random.randint(0, 2),
            tampering_attempts=random.randint(0, 5),
            spoofing_attempts=random.randint(0, 4),
            anomaly_score=round(random.uniform(0.0, 1.0), 2),
            battery_level=round(random.uniform(10.0, 100.0), 2),
            status=random.choice(["active", "compromised", "alerting"])
        )
        put_item(data, "threat", dynamodb)


def seed_plant_data():
    for i in range(5):
        data = PlantData(
            sensor_id=f"plant-{1000 + i}",
            leaf_moisture=round(random.uniform(30.0, 80.0), 2),
            chlorophyll_level=round(random.uniform(20.0, 70.0), 2),
            growth_rate=round(random.uniform(0.5, 2.0), 2),
            disease_risk=round(random.uniform(0.0, 1.0), 2),
            stem_diameter=round(random.uniform(0.2, 2.0), 2),
            battery_level=round(random.uniform(10.0, 100.0), 2),
            status=random.choice(["healthy", "wilting", "diseased"])
        )
        put_item(data, "plant", dynamodb)


def seed_all():
    seed_soil_data()
    seed_atmospheric_data()
    seed_water_data()
    seed_threat_data()
    seed_plant_data()
    print("✅ All sensor data seeded successfully.")


def put_item(table_name: str, item: dict):
    table = dynamodb.Table(table_name)
    table.put_item(Item=item)

if __name__ == "__main__":
    seed_all()
