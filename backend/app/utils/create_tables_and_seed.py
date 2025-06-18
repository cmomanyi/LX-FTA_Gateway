import boto3
from botocore.exceptions import ClientError

from app.utils.seed_sensors import seed_all

# Use local AWS credentials
session = boto3.Session(profile_name="default", region_name="us-east-1")
dynamodb = session.client("dynamodb")

# Table names mapped to primary key
TABLE_DEFINITIONS = {
    "lx-fta-soil-data": "sensor_id",
    "lx-fta-atmospheric-data": "sensor_id",
    "lx-fta-water-data": "sensor_id",
    "lx-fta-threat-data": "sensor_id",
    "lx-fta-plant-data": "sensor_id",
}


def table_exists(table_name):
    try:
        dynamodb.describe_table(TableName=table_name)
        return True
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            return False
        else:
            raise


def create_table(table_name, partition_key):
    print(f"🔧 Creating table {table_name}...")
    dynamodb.create_table(
        TableName=table_name,
        KeySchema=[
            {"AttributeName": partition_key, "KeyType": "HASH"},
        ],
        AttributeDefinitions=[
            {"AttributeName": partition_key, "AttributeType": "S"},
        ],
        BillingMode="PAY_PER_REQUEST",
    )

    # Wait for table to become active
    waiter = dynamodb.get_waiter("table_exists")
    waiter.wait(TableName=table_name)
    print(f"✅ Table {table_name} is ready.")


def create_tables_if_not_exist():
    for table_name, partition_key in TABLE_DEFINITIONS.items():
        if table_exists(table_name):
            print(f"✔️ Table {table_name} already exists.")
        else:
            create_table(table_name, partition_key)


if __name__ == "__main__":
    create_tables_if_not_exist()
    seed_all()
