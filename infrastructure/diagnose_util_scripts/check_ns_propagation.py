import boto3
import json

# Replace with your actual values
role_name = "GitHubActionsDeployRole"
bucket_name = "lx-fta-frontend-gdwib5"
policy_name = "FrontendS3AccessPolicy"

# Create IAM client
iam = boto3.client("iam")

# Define the inline policy
policy_document = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowS3AccessForFrontend",
            "Effect": "Allow",
            "Action": [
                "s3:ListBucket",
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject"
            ],
            "Resource": [
                f"arn:aws:s3:::{bucket_name}",
                f"arn:aws:s3:::{bucket_name}/*"
            ]
        }
    ]
}

# Attach policy to IAM role
try:
    iam.put_role_policy(
        RoleName=role_name,
        PolicyName=policy_name,
        PolicyDocument=json.dumps(policy_document)
    )
    print(f"✅ Successfully attached policy '{policy_name}' to role '{role_name}'")
except Exception as e:
    print(f"❌ Failed to attach policy: {e}")
