import boto3
import json

# === CONFIGURATION ===
role_name = "GitHubActionsAdminDeployRole"
policy_name = "GitHubAdminInfraDeploymentPolicy"
account_id = "263307268672"
repo_subject = "repo:cmomanyi/LX-FTA_Gateway:ref:refs/heads/main"

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

# === POLICY DOCUMENT ===
policy_document = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:*",
                "cloudfront:*",
                "route53:*",
                "acm:*",
                "iam:PassRole"
            ],
            "Resource": "*"
        }
    ]
}

# === CREATE ROLE ===
try:
    response = iam.create_role(
        RoleName=role_name,
        AssumeRolePolicyDocument=json.dumps(trust_policy),
        Description="Allows GitHub Actions to manage infrastructure like S3, CloudFront, Route53"
    )
    print(f"✅ Role created: {response['Role']['Arn']}")
except iam.exceptions.EntityAlreadyExistsException:
    print(f"⚠️ Role '{role_name}' already exists.")

# === CREATE POLICY ===
try:
    policy_response = iam.create_policy(
        PolicyName=policy_name,
        PolicyDocument=json.dumps(policy_document),
        Description="Admin policy for frontend infra deployment"
    )
    policy_arn = policy_response["Policy"]["Arn"]
    print(f"✅ Policy created: {policy_arn}")
except iam.exceptions.EntityAlreadyExistsException:
    policy_arn = f"arn:aws:iam::{account_id}:policy/{policy_name}"
    print(f"⚠️ Policy '{policy_name}' already exists. Using ARN: {policy_arn}")

# === ATTACH POLICY TO ROLE ===
iam.attach_role_policy(RoleName=role_name, PolicyArn=policy_arn)
print(f"✅ Attached policy to role: {role_name}")
