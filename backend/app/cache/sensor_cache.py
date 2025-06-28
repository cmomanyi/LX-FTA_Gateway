# sensor_cache.py

from typing import Set, Dict, List
from collections import defaultdict

# ✅ In-memory cache for known sensor IDs
sensor_id_cache: Set[str] = set()

# ✅ In-memory cache for latest sensor data by type
latest_data_cache: Dict[str, List] = defaultdict(list)


# You can optionally add:
# - timestamp of last cache update
# - helper methods to refresh or clear the cache

# Example helper function

def update_sensor_id_cache_from_data():
    global sensor_id_cache
    sensor_id_cache = {sensor.sensor_id for sensors in latest_data_cache.values() for sensor in sensors}
