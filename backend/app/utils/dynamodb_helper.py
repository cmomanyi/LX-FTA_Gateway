# app/utils/dynamodb_helper.py

import boto3
from boto3.dynamodb.conditions import Key
from decimal import Decimal
from typing import Type, List

dynamodb = boto3.resource("dynamodb", region_name="us-east-1")


def get_table(sensor_type: str):
    return dynamodb.Table(f"lx-fta-{sensor_type}-data")


def float_to_decimal(data: dict) -> dict:
    return {
        k: Decimal(str(v)) if isinstance(v, float) else v
        for k, v in data.items()
    }


def get_all_items(model: Type, sensor_type: str) -> List:
    table = get_table(sensor_type)
    response = table.scan()
    items = response.get("Items", [])
    return [model(**item) for item in items]


def put_item(model_instance, sensor_type: str):
    table = get_table(sensor_type)
    item = model_instance.dict()
    table.put_item(Item=float_to_decimal(item))
