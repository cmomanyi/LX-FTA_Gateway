import boto3

iam = boto3.client('iam')
role_name = "GitHubActionsDeployRole"
account_id = boto3.client("sts").get_caller_identity()["Account"]
role_arn = f"arn:aws:iam::{account_id}:role/{role_name}"

# Actions to verify
actions_to_check = [
    "s3:GetObject",
    "s3:PutObject",
    "cloudfront:CreateDistribution",
    "cloudfront:TagResource",
    "route53:ChangeResourceRecordSets",
    "ecr:InitiateLayerUpload",
    "ecr:ListTagsForResource",
    "ecs:DescribeClusters",
    "logs:DescribeLogGroups",
    "iam:GetRolePolicy",
    "iam:ListAttachedRolePolicies",
    "iam:ListRolePolicies",
    "elasticloadbalancing:DescribeListeners",
    "elasticloadbalancing:DescribeTargetGroupAttributes",
    "dynamodb:ListTagsOfResource",
    "dynamodb:DescribeContinuousBackups"
]

# Run simulation
response = iam.simulate_principal_policy(
    PolicySourceArn=role_arn,
    ActionNames=actions_to_check
)

# Display results
print("🔍 Permission check for GitHubActionsDeployRole:")
for result in response['EvaluationResults']:
    action = result['EvalActionName']
    decision = result['EvalDecision']
    print(f" - {action}: {'✅ ALLOWED' if decision == 'allowed' else '❌ DENIED'}")
