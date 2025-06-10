import boto3
import json

iam = boto3.client("iam")
account_id = boto3.client("sts").get_caller_identity()["Account"]
role_name = "GitHubActionsDeployRole"
policy_name = "GitHubActionsMissingPermsPolicy"

policy_document = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "cloudfront:CreateDistribution",
                "route53:ChangeResourceRecordSets",
                "iam:ListAttachedRolePolicies",
                "elasticloadbalancing:DescribeListeners",
                "dynamodb:ListTagsOfResource"
            ],
            "Resource": "*"
        }
    ]
}

# Check if policy already exists
policy_arn = f"arn:aws:iam::{account_id}:policy/{policy_name}"
try:
    iam.get_policy(PolicyArn=policy_arn)
    print(f"ℹ️ Policy '{policy_name}' already exists.")
except iam.exceptions.NoSuchEntityException:
    print("📌 Creating new policy...")
    iam.create_policy(
        PolicyName=policy_name,
        PolicyDocument=json.dumps(policy_document)
    )

# Attach policy to role
try:
    iam.attach_role_policy(RoleName=role_name, PolicyArn=policy_arn)
    print(f"🔗 Policy '{policy_name}' successfully attached to '{role_name}'.")
except Exception as e:
    print(f"❌ Failed to attach policy: {e}")
