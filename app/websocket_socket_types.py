import random


def generate_sensor_data(sensor_type: str, user: str):
    sensor_id = f"{sensor_type}-{random.randint(1000, 9999)}"

    if sensor_type == "soil":
        return {
            "sensor_id": sensor_id,
            "user": user,
            "temperature": round(random.uniform(15.0, 35.0), 2),
            "moisture": round(random.uniform(20.0, 80.0), 2),
            "status": random.choice(["active", "sleeping", "compromised"]),
        }

    elif sensor_type == "water":
        return {
            "sensor_id": sensor_id,
            "user": user,
            "flow_rate": round(random.uniform(5.0, 15.0), 2),
            "water_level": round(random.uniform(10.0, 45.0), 2),
            "status": random.choice(["active", "compromised"]),
        }

    elif sensor_type == "threat":
        return {
            "sensor_id": sensor_id,
            "user": user,
            "anomaly_score": round(random.uniform(0.0, 1.0), 2),
            "tampering": random.choice([True, False]),
            "jamming": random.choice([True, False]),
            "status": random.choice(["active", "alert"]),
        }

    elif sensor_type == "atmospheric":
        return {
            "sensor_id": sensor_id,
            "user": user,
            "air_temp": round(random.uniform(10.0, 40.0), 2),
            "humidity": round(random.uniform(30.0, 90.0), 2),
            "co2": round(random.uniform(300.0, 600.0), 2),
            "status": random.choice(["active", "error"]),
        }

    elif sensor_type == "plant":
        return {
            "sensor_id": sensor_id,
            "user": user,
            "chlorophyll": round(random.uniform(20.0, 50.0), 2),
            "leaf_moisture": round(random.uniform(30.0, 70.0), 2),
            "growth_rate": round(random.uniform(0.5, 2.0), 2),
            "status": random.choice(["healthy", "wilting", "diseased"]),
        }

    return {"error": "Invalid sensor type"}
