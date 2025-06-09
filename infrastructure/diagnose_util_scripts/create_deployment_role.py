import boto3
import json

# === CONFIGURATION ===
role_name = "GitHubActionsDeployRole"
policy_name = "GitHubDeployFrontendPolicy"
bucket_name = "lx-fta-frontend-"  # update this if needed
repo_subject = "repo:cmomanyi/LX-FTA_Gateway:ref:refs/heads/main"
account_id = "263307268672"

iam = boto3.client("iam")

# === TRUST POLICY ===
trust_policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Federated": f"arn:aws:iam::{account_id}:oidc-provider/token.actions.githubusercontent.com"
            },
            "Action": "sts:AssumeRoleWithWebIdentity",
            "Condition": {
                "StringEquals": {
                    "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
                    "token.actions.githubusercontent.com:sub": repo_subject
                }
            }
        }
    ]
}

# === INLINE POLICY ===
policy_document = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": ["s3:*"],
            "Resource": [
                f"arn:aws:s3:::{bucket_name}",
                f"arn:aws:s3:::{bucket_name}/*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": ["cloudfront:CreateInvalidation"],
            "Resource": "*"
        }
    ]
}

# === CREATE ROLE ===
try:
    response = iam.create_role(
        RoleName=role_name,
        AssumeRolePolicyDocument=json.dumps(trust_policy),
        Description="Allows GitHub Actions to deploy frontend to S3 and invalidate CloudFront cache"
    )
    print(f"✅ Role created: {response['Role']['Arn']}")
except iam.exceptions.EntityAlreadyExistsException:
    print(f"⚠️ Role '{role_name}' already exists.")

# === CREATE POLICY ===
try:
    policy_response = iam.create_policy(
        PolicyName=policy_name,
        PolicyDocument=json.dumps(policy_document),
        Description="Policy for GitHub frontend deployment to S3/CloudFront"
    )
    policy_arn = policy_response['Policy']['Arn']
    print(f"✅ Policy created: {policy_arn}")
except iam.exceptions.EntityAlreadyExistsException:
    policy_arn = f"arn:aws:iam::{account_id}:policy/{policy_name}"
    print(f"⚠️ Policy '{policy_name}' already exists. Using ARN: {policy_arn}")

# === ATTACH POLICY TO ROLE ===
iam.attach_role_policy(RoleName=role_name, PolicyArn=policy_arn)
print(f"✅ Attached policy to role: {role_name}")
