import boto3
import json

# Constants – update as needed
AWS_ACCOUNT_ID = "263307268672"
ROLE_NAME = "GitHubActionsDeployRole"
POLICY_NAME = "FrontendS3AccessPolicy"
FRONTEND_BUCKET = "lx-fta-frontend"

iam = boto3.client("iam")

# Build IAM policy
policy_document = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": ["s3:ListBucket"],
            "Resource": f"arn:aws:s3:::{FRONTEND_BUCKET}"
        },
        {
            "Effect": "Allow",
            "Action": ["s3:*"],
            "Resource": f"arn:aws:s3:::{FRONTEND_BUCKET}/*"
        },
        {
            "Effect": "Allow",
            "Action": ["cloudfront:CreateInvalidation"],
            "Resource": "*"
        }
    ]
}

# Attach inline policy
response = iam.put_role_policy(
    RoleName=ROLE_NAME,
    PolicyName=POLICY_NAME,
    PolicyDocument=json.dumps(policy_document)
)

print("✅ Successfully updated policy:")
print(json.dumps(policy_document, indent=2))
