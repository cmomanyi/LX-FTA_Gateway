from decimal import Decimal
import boto3

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
