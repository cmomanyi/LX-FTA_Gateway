import boto3
from botocore.exceptions import ClientError

region = "us-east-1"
dynamodb_table_name = "lx-fta-audit-logs"
log_group_name = "/ecs/lx-fta-backend"

dynamodb = boto3.client("dynamodb", region_name=region)
logs = boto3.client("logs", region_name=region)

def create_dynamodb_table():
    try:
        existing = dynamodb.describe_table(TableName=dynamodb_table_name)
        print(f"⚠️ DynamoDB table '{dynamodb_table_name}' already exists.")
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            print(f"🛠️ Creating DynamoDB table '{dynamodb_table_name}'...")
            dynamodb.create_table(
                TableName=dynamodb_table_name,
                AttributeDefinitions=[{
                    "AttributeName": "id",
                    "AttributeType": "S"
                }],
                KeySchema=[{
                    "AttributeName": "id",
                    "KeyType": "HASH"
                }],
                BillingMode="PAY_PER_REQUEST"
            )
            print("✅ DynamoDB table created.")
        else:
            raise

def create_log_group():
    log_groups = logs.describe_log_groups(logGroupNamePrefix=log_group_name).get("logGroups", [])
    if any(lg["logGroupName"] == log_group_name for lg in log_groups):
        print(f"⚠️ Log group '{log_group_name}' already exists.")
    else:
        print(f"🛠️ Creating CloudWatch log group '{log_group_name}'...")
        logs.create_log_group(logGroupName=log_group_name)
        print("✅ Log group created.")


if __name__ == "__main__":
    create_dynamodb_table()
    create_log_group()
