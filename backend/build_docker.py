import boto3
import json

log_group_name = "/ecs/lx-fta-backend"
region = "us-east-1"
role_name = "ecsTaskExecutionRole"

# Create clients
logs_client = boto3.client("logs", region_name=region)
iam_client = boto3.client("iam")

# Create log group if it doesn't exist
try:
    logs_client.create_log_group(logGroupName=log_group_name)
    print(f"✅ Log group '{log_group_name}' created.")
except logs_client.exceptions.ResourceAlreadyExistsException:
    print(f"ℹ️ Log group '{log_group_name}' already exists.")

# Attach inline policy to allow ECS to write logs
policy_document = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "*"
        }
    ]
}

try:
    iam_client.put_role_policy(
        RoleName=role_name,
        PolicyName="AllowECSCloudWatchLogging",
        PolicyDocument=json.dumps(policy_document)
    )
    print(f"✅ Attached 'AllowECSCloudWatchLogging' to role '{role_name}'.")
except Exception as e:
    print(f"❌ Failed to attach policy: {e}")
