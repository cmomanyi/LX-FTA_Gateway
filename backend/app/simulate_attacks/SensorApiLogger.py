from fastapi import HTTPException
from app.cache.sensor_cache import sensor_id_cache


class SensorApiLogger:
    @staticmethod
    def validate_sensor_id(sensor_id: str) -> bool:
        if sensor_id not in sensor_id_cache:
            raise HTTPException(status_code=400, detail="Invalid sensor ID")
        return True

    @staticmethod
    def list_all_sensor_ids() -> list:
        return list(sensor_id_cache)

    @staticmethod
    def is_sensor_id_valid(sensor_id: str) -> bool:
        return sensor_id in sensor_id_cache
