import boto3
import json

# Initialize the IAM client
iam = boto3.client("iam")

# Configuration
policy_name = "GitHubActionsExtraAccessPolicy"
role_name = "GitHubActionsDeployRole"
account_id = "263307268672"  # Replace with your actual AWS Account ID

# Policy definition
policy_document = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "iam:ListRolePolicies",
                "elasticloadbalancing:DescribeLoadBalancers",
                "elasticloadbalancing:DescribeTargetGroupAttributes",
                "dynamodb:DescribeContinuousBackups"
            ],
            "Resource": "*"
        }
    ]
}

try:
    print(f"🔧 Creating IAM policy: {policy_name}")
    response = iam.create_policy(
        PolicyName=policy_name,
        PolicyDocument=json.dumps(policy_document)
    )
    policy_arn = response['Policy']['Arn']
    print(f"✅ Created policy: {policy_arn}")
except iam.exceptions.EntityAlreadyExistsException:
    policy_arn = f"arn:aws:iam::{account_id}:policy/{policy_name}"
    print(f"ℹ️ Policy already exists, using ARN: {policy_arn}")

try:
    print(f"🔗 Attaching policy to role: {role_name}")
    iam.attach_role_policy(RoleName=role_name, PolicyArn=policy_arn)
    print("✅ Successfully attached policy.")
except Exception as e:
    print(f"❌ Failed to attach policy: {e}")
