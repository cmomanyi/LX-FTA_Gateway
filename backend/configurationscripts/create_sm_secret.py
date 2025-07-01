import boto3
import json

# === Configuration ===
aws_region = "us-east-1"
role_name = "ecsTaskExecutionRole"
table_arn = "arn:aws:dynamodb:us-east-1:263307268672:table/lx-fta-audit-logs"
policy_name = "AllowDynamoDBWriteAccess"

# === Policy Document ===
policy_document = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:BatchWriteItem",
                "dynamodb:PutItem",
                "dynamodb:UpdateItem"
            ],
            "Resource": table_arn
        }
    ]
}

# === Attach Inline Policy ===
def attach_inline_policy():
    iam = boto3.client("iam", region_name=aws_region)

    try:
        print(f"📌 Attaching policy '{policy_name}' to role '{role_name}'...")
        response = iam.put_role_policy(
            RoleName=role_name,
            PolicyName=policy_name,
            PolicyDocument=json.dumps(policy_document)
        )
        print("✅ Policy attached successfully.")
    except Exception as e:
        print("❌ Failed to attach policy:", e)

if __name__ == "__main__":
    attach_inline_policy()
