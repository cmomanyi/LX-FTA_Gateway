import boto3
import json
import time

iam = boto3.client('iam')
role_name = "GitHubActionsDeployRole"
policy_name = "GitHubActionsFullDeployPolicy"

# Add missing permissions
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
                "ecr:*",
                "ecs:*",
                "logs:*",
                "iam:GetRole",
                "iam:ListRolePolicies",
                "iam:GetRolePolicy",
                "iam:ListAttachedRolePolicies",
                "iam:AttachRolePolicy",
                "ec2:Describe*",
                "elasticloadbalancing:*",
                "dynamodb:*"
            ],
            "Resource": "*"
        }
    ]
}

# Create or update policy
try:
    response = iam.create_policy(
        PolicyName=policy_name,
        PolicyDocument=json.dumps(policy_document)
    )
    policy_arn = response['Policy']['Arn']
    print(f"✅ Created new policy: {policy_arn}")
except iam.exceptions.EntityAlreadyExistsException:
    policy_arn = f"arn:aws:iam::{boto3.client('sts').get_caller_identity()['Account']}:policy/{policy_name}"
    print(f"ℹ️ Policy already exists. Using existing ARN: {policy_arn}")

# Attach policy to role
try:
    iam.attach_role_policy(RoleName=role_name, PolicyArn=policy_arn)
    print(f"🔗 Successfully attached policy to {role_name}")
except Exception as e:
    print(f"❌ Failed to attach policy: {e}")
