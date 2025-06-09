import boto3
import json

# Set these values accordingly
role_name = "GitHubActionsDeployRole"
aws_account_id = "263307268672"
github_repo = "your-username/your-repo-name"  # ⚠️ Replace with actual GitHub repo name

# Define the OIDC trust policy for GitHub Actions
trust_policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Federated": f"arn:aws:iam::{aws_account_id}:oidc-provider/token.actions.githubusercontent.com"
            },
            "Action": "sts:AssumeRoleWithWebIdentity",
            "Condition": {
                "StringLike": {
                    "token.actions.githubusercontent.com:sub": f"repo:{github_repo}:*"
                }
            }
        }
    ]
}

# Create a Boto3 IAM client
iam = boto3.client('iam')

# Update the assume role policy
response = iam.update_assume_role_policy(
    RoleName=role_name,
    PolicyDocument=json.dumps(trust_policy)
)

print("✅ Trust policy updated for:", role_name)
