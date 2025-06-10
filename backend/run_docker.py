import boto3
import json

ROLE_NAME = "GitHubActionsDeployRole"
POLICY_NAME = "FrontendS3CloudFrontPolicy"
BUCKET_NAME = "your-bucket-name"
REGION = "us-east-1"

policy_document = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "S3BucketAccess",
            "Effect": "Allow",
            "Action": [
                "s3:ListBucket"
            ],
            "Resource": f"arn:aws:s3:::{BUCKET_NAME}"
        },
        {
            "Sid": "S3ObjectAccess",
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject"
            ],
            "Resource": f"arn:aws:s3:::{BUCKET_NAME}/*"
        },
        {
            "Sid": "CloudFrontInvalidation",
            "Effect": "Allow",
            "Action": [
                "cloudfront:CreateInvalidation"
            ],
            "Resource": "*"
        }
    ]
}

def attach_inline_policy():
    iam = boto3.client("iam", region_name=REGION)
    try:
        response = iam.put_role_policy(
            RoleName=ROLE_NAME,
            PolicyName=POLICY_NAME,
            PolicyDocument=json.dumps(policy_document)
        )
        print("✅ IAM policy attached to role.")
    except Exception as e:
        print("❌ Failed to attach policy:", str(e))

if __name__ == "__main__":
    attach_inline_policy()
