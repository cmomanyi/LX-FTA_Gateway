from decimal import Decimal
import boto3
import uuid
from datetime import datetime

dynamodb = boto3.resource("dynamodb", region_name="us-east-1")


def convert_floats_to_decimal(obj):
    if isinstance(obj, list):
        return [convert_floats_to_decimal(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: convert_floats_to_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, float):
        return Decimal(str(obj))  # convert to string first to avoid precision errors
    else:
        return obj


def put_item(table_name: str, item: dict):
    table = dynamodb.Table(table_name)
    safe_item = convert_floats_to_decimal(item)
    table.put_item(Item=safe_item)


def log_access(sensor_type: str, endpoint: str, client_ip: str):
    table = dynamodb.Table("lx-fta-access-logs")
    item = {
        "id": str(uuid.uuid4()),
        "sensor_type": sensor_type,
        "endpoint": endpoint,
        "client_ip": client_ip,
        "timestamp": datetime.utcnow().isoformat()
    }
    table.put_item(Item=item)
