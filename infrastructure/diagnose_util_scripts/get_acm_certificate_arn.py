import boto3
import json

# Parameters
role_name = "GitHubActionsDeployRole"
policy_name = "GitHubActionsFullDeployPolicy"
policy_document = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "S3Access",
            "Effect": "Allow",
            "Action": [
                "s3:ListBucket",
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject"
            ],
            "Resource": [
                "arn:aws:s3:::lx-fta-frontend*",
                "arn:aws:s3:::lx-fta-frontend*/*"
            ]
        },
        {
            "Sid": "CloudFrontAccess",
            "Effect": "Allow",
            "Action": [
                "cloudfront:CreateInvalidation",
                "cloudfront:GetDistribution",
                "cloudfront:UpdateDistribution",
                "cloudfront:CreateDistribution",
                "cloudfront:CreateOriginAccessControl"
            ],
            "Resource": "*"
        },
        {
            "Sid": "IAMAccess",
            "Effect": "Allow",
            "Action": [
                "iam:PassRole",
                "iam:GetRole",
                "iam:CreateRole",
                "iam:AttachRolePolicy",
                "iam:CreatePolicy",
                "iam:GetPolicy"
            ],
            "Resource": "*"
        }
    ]
}

# Create IAM client
iam = boto3.client('iam')

# Create the policy
try:
    response = iam.create_policy(
        PolicyName=policy_name,
        PolicyDocument=json.dumps(policy_document),
        Description="Policy for GitHub Actions to deploy frontend and backend",
    )
    policy_arn = response['Policy']['Arn']
    print(f"✅ Created policy: {policy_arn}")
except iam.exceptions.EntityAlreadyExistsException:
    account_id = boto3.client('sts').get_caller_identity().get('Account')
    policy_arn = f"arn:aws:iam::{account_id}:policy/{policy_name}"
    print(f"⚠️ Policy already exists: {policy_arn}")

# Attach the policy to the role
try:
    iam.attach_role_policy(
        RoleName=role_name,
        PolicyArn=policy_arn
    )
    print(f"✅ Attached policy to role: {role_name}")
except Exception as e:
    print(f"❌ Failed to attach policy: {e}")
