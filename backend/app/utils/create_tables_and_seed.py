# app/utils/create_tables_and_seed.py

import boto3
from botocore.exceptions import ClientError
from time import sleep
from seed_sensors import seed_all
dynamodb = boto3.client("dynamodb", region_name="us-east-1")

TABLES = {
    "soil": "lx-fta-soil-data",
    "atmospheric": "lx-fta-atmospheric-data",
    "water": "lx-fta-water-data",
    "threat": "lx-fta-threat-data",
    "plant": "lx-fta-plant-data"
}

def table_exists(table_name):
    try:
        dynamodb.describe_table(TableName=table_name)
        return True
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            return False
        raise

def create_table_if_not_exists(table_name):
    if table_exists(table_name):
        print(f"✔️ Table '{table_name}' already exists.")
        return

    print(f"⏳ Creating table '{table_name}'...")
    dynamodb.create_table(
        TableName=table_name,
        KeySchema=[{"AttributeName": "sensor_id", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "sensor_id", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST"
    )

    # Wait for table to become active
    waiter = boto3.client("dynamodb", region_name="us-east-1").get_waiter("table_exists")
    waiter.wait(TableName=table_name)
    print(f"✅ Table '{table_name}' created and ready.")

def create_all_tables():
    for sensor_type, table_name in TABLES.items():
        create_table_if_not_exists(table_name)

if __name__ == "__main__":
    create_all_tables()
    print("🚀 Proceeding to seed sensor data...\n")
    seed_all()
