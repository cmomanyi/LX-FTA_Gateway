import boto3
import json

role_name = "GitHubActionsDeployRole"
policy_name = "GitHubFullDeployPolicy"

policy_doc = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "cloudfront:*",
                "iam:CreatePolicy",
                "iam:CreateRole",
                "iam:AttachRolePolicy",
                "iam:PassRole",
                "iam:GetRole",
                "iam:GetPolicy",
                "iam:UpdateAssumeRolePolicy",
                "s3:*",
                "ecr:*",
                "ecs:*",
                "secretsmanager:GetSecretValue",
                "logs:*",
                "ec2:DescribeSecurityGroups",
                "elasticloadbalancing:DescribeTargetGroups",
                "dynamodb:DescribeTable"
            ],
            "Resource": "*"
        }
    ]
}

iam = boto3.client("iam")
sts = boto3.client("sts")
account_id = sts.get_caller_identity()["Account"]
policy_arn = f"arn:aws:iam::{account_id}:policy/{policy_name}"

# Create or skip policy
try:
    iam.create_policy(
        PolicyName=policy_name,
        PolicyDocument=json.dumps(policy_doc),
        Description="Policy for full GitHub Actions deployment permissions"
    )
    print("✅ Policy created.")
except iam.exceptions.EntityAlreadyExistsException:
    print("⚠️ Policy already exists.")

# Attach to role
iam.attach_role_policy(RoleName=role_name, PolicyArn=policy_arn)
print(f"✅ Attached policy to role: {role_name}")
