import boto3
import json

# Initialize IAM client
iam = boto3.client('iam')

# Define role and policy
role_name = "GitHubActionsDeployRole"
policy_name = "GitHubActionsELBPermissions"

# Permissions to be granted
policy_document = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "elasticloadbalancing:DescribeListeners",
                "elasticloadbalancing:DescribeListenerAttributes"
            ],
            "Resource": "*"
        }
    ]
}

# Apply inline policy
try:
    iam.put_role_policy(
        RoleName=role_name,
        PolicyName=policy_name,
        PolicyDocument=json.dumps(policy_document)
    )
    print(f"✅ Successfully attached inline policy '{policy_name}' to role '{role_name}'.")
except Exception as e:
    print(f"❌ Failed to attach policy: {e}")
