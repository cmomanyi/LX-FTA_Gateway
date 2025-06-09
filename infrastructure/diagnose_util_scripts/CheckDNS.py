import boto3

iam = boto3.client("iam")
role_name = "GitHubActionsDeployRole"

attached = iam.list_attached_role_policies(RoleName=role_name)
print(f"Policies attached to {role_name}:\n")
for policy in attached['AttachedPolicies']:
    print(f"- {policy['PolicyName']} (ARN: {policy['PolicyArn']})")
