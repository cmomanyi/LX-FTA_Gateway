import boto3
import json

iam = boto3.client("iam")
sts = boto3.client("sts")

# Fallback default region if boto3 returns None
region = boto3.session.Session().region_name or "us-east-1"
account_id = sts.get_caller_identity()["Account"]

tables = [
    "lx-fta-soil-data",
    "lx-fta-atmospheric-data",
    "lx-fta-water-data",
    "lx-fta-threat-data",
    "lx-fta-plant-data",
    "lx-fta-audit-logs"
]

table_arns = [f"arn:aws:dynamodb:{region}:{account_id}:table/{t}" for t in tables]

policy_document = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowReadWriteScan",
            "Effect": "Allow",
            "Action": [
                "dynamodb:GetItem",
                "dynamodb:PutItem",
                "dynamodb:UpdateItem",
                "dynamodb:Scan"
            ],
            "Resource": table_arns
        }
    ]
}

policy_json = json.dumps(policy_document, indent=2)

print("🔍 Final policy to be applied:")
print(policy_json)

response = iam.put_role_policy(
    RoleName="ecsTaskExecutionRole",
    PolicyName="AllowSensorDynamoDBAccess",
    PolicyDocument=policy_json
)

print("✅ Policy successfully applied.")
