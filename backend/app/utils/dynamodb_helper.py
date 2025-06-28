

from decimal import Decimal
import boto3

from datetime import datetime
from botocore.exceptions import ClientError
import uuid

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


# def put_item(table_name: str, item: dict):
#     table = dynamodb.Table(table_name)
#     safe_item = convert_floats_to_decimal(item)
#     table.put_item(Item=safe_item)



def put_item(table_name: str, item: dict):
    if 'id' not in item:
        item['id'] = str(uuid.uuid4())  # ✅ Add a unique ID if missing

    table = dynamodb.Table(table_name)
    safe_item = convert_floats_to_decimal(item)
    table.put_item(Item=safe_item)


def scan_table(table_name: str):
    """
    Scan a DynamoDB table and return all items.
    """
    try:
        table = dynamodb.Table(table_name)
        items = []
        response = table.scan()
        items.extend(response.get("Items", []))
        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            items.extend(response.get("Items", []))
        return items
    except ClientError as e:
        print(f"❌ Failed to scan table {table_name}: {e}")
        return []


def fetch_sensor_ids_from_table(table_name: str) -> set:
    """
    Returns all sensor IDs from a given table.
    """
    items = scan_table(table_name)
    return {item["sensor_id"] for item in items if "sensor_id" in item}


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


AUDIT_TABLE_NAME = "lx-fta-audit-logs"


def put_alert_to_audit_log(alert: dict) -> bool:
    try:
        table = dynamodb.Table(AUDIT_TABLE_NAME)
        table.put_item(Item=alert)
        return True
    except ClientError as e:
        print(f"❌ Error saving alert to audit logs: {e}")
        return False


def get_recent_audit_logs(limit=10):
    table = dynamodb.Table(AUDIT_TABLE_NAME)
    response = table.scan(Limit=limit)
    return response.get("Items", [])
