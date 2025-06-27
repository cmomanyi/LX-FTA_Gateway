import boto3
import os
import uuid
from datetime import datetime
from botocore.exceptions import ClientError

# DynamoDB setup
dynamodb = boto3.resource("dynamodb", region_name=os.getenv("AWS_REGION", "us-east-1"))
table_name = os.getenv("DYNAMODB_TABLE", "lx_fta_audit_logs")
table = dynamodb.Table(table_name)

# S3 setup
s3 = boto3.client("s3", region_name=os.getenv("AWS_REGION", "us-east-1"))
s3_bucket = os.getenv("S3_BUCKET_NAME", "lx-fta-firmware-bucket")

# Secrets Manager setup
secrets_client = boto3.client("secretsmanager", region_name=os.getenv("AWS_REGION", "us-east-1"))


def dynamodb_put_item(payload: dict):
    """Insert a record into DynamoDB."""
    item = {
        "sensor_id": payload.get("sensor_id", str(uuid.uuid4())),
        "timestamp": datetime.utcnow().isoformat(),
        **payload,
    }
    table.put_item_db(Item=item)
    return item


def dynamodb_query_logs(sensor_id: str):
    """Query logs by sensor_id."""
    response = table.query(
        KeyConditionExpression=boto3.dynamodb.conditions.Key("sensor_id").eq(sensor_id)
    )
    return response.get("Items", [])


def upload_to_s3(file_content: bytes, filename: str):
    """Upload a firmware file to S3."""
    key = f"firmware/{datetime.utcnow().strftime('%Y%m%d')}/{filename}"
    s3.put_object(Bucket=s3_bucket, Key=key, Body=file_content)
    s3_url = f"https://{s3_bucket}.s3.amazonaws.com/{key}"
    return s3_url


def get_secret(secret_name: str):
    """Retrieve a secret from AWS Secrets Manager."""
    try:
        response = secrets_client.get_secret_value(SecretId=secret_name)
        return response.get("SecretString")
    except ClientError as e:
        raise Exception(f"Failed to retrieve secret: {str(e)}")
