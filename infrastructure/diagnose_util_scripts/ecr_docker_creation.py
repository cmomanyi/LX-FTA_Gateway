import boto3
import json

ROLE_NAME = "GitHubActionsDeployRole"
POLICY_NAME = "FrontendS3AccessPolicy"
BUCKET_NAME = "portal.lx-gateway.tech"  # Update this to your actual bucket name

policy_document = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowListBucket",
            "Effect": "Allow",
            "Action": ["s3:ListBucket"],
            "Resource": f"arn:aws:s3:::{BUCKET_NAME}"
        },
        {
            "Sid": "AllowPutDeleteObjects",
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:PutObjectAcl",
                "s3:DeleteObject"
            ],
            "Resource": f"arn:aws:s3:::{BUCKET_NAME}/*"
        }
    ]
}

def attach_policy():
    iam = boto3.client('iam')
    iam.put_role_policy(
        RoleName=ROLE_NAME,
        PolicyName=POLICY_NAME,
        PolicyDocument=json.dumps(policy_document)
    )
    print(f"✅ Policy '{POLICY_NAME}' attached to role '{ROLE_NAME}' for bucket '{BUCKET_NAME}'")

if __name__ == "__main__":
    attach_policy()
