import boto3
import json

iam = boto3.client('iam')

policy_name = "GitHubActionsFullDeployPolicy"
role_name = "GitHubActionsDeployRole"

policy_document = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "S3FullAccess",
            "Effect": "Allow",
            "Action": ["s3:Get*", "s3:Put*", "s3:List*"],
            "Resource": [
                "arn:aws:s3:::lx-fta-frontend",
                "arn:aws:s3:::lx-fta-frontend/*"
            ]
        },
        {
            "Sid": "CloudFrontPermissions",
            "Effect": "Allow",
            "Action": [
                "cloudfront:CreateDistribution",
                "cloudfront:UpdateDistribution",
                "cloudfront:GetDistribution",
                "cloudfront:TagResource",
                "cloudfront:ListDistributions"
            ],
            "Resource": "*"
        },
        {
            "Sid": "ECRPermissions",
            "Effect": "Allow",
            "Action": [
                "ecr:GetAuthorizationToken",
                "ecr:BatchCheckLayerAvailability",
                "ecr:GetDownloadUrlForLayer",
                "ecr:BatchGetImage",
                "ecr:PutImage",
                "ecr:InitiateLayerUpload",
                "ecr:UploadLayerPart",
                "ecr:CompleteLayerUpload",
                "ecr:ListTagsForResource",
                "ecr:DescribeRepositories"
            ],
            "Resource": "*"
        },
        {
            "Sid": "CloudWatchLogs",
            "Effect": "Allow",
            "Action": [
                "logs:DescribeLogGroups",
                "logs:ListTagsForResource"
            ],
            "Resource": "*"
        },
        {
            "Sid": "IAMPermissions",
            "Effect": "Allow",
            "Action": [
                "iam:GetRole",
                "iam:ListRolePolicies"
            ],
            "Resource": "*"
        },
        {
            "Sid": "ELBPermissions",
            "Effect": "Allow",
            "Action": [
                "elasticloadbalancing:DescribeLoadBalancers",
                "elasticloadbalancing:DescribeTargetGroups",
                "elasticloadbalancing:DescribeTargetGroupAttributes"
            ],
            "Resource": "*"
        },
        {
            "Sid": "DynamoDBDescribe",
            "Effect": "Allow",
            "Action": [
                "dynamodb:DescribeTable",
                "dynamodb:DescribeContinuousBackups"
            ],
            "Resource": "*"
        }
    ]
}

# Create policy
try:
    print("📌 Creating policy...")
    policy_response = iam.create_policy(
        PolicyName=policy_name,
        PolicyDocument=json.dumps(policy_document)
    )
    policy_arn = policy_response["Policy"]["Arn"]
    print(f"✅ Policy created: {policy_arn}")
except iam.exceptions.EntityAlreadyExistsException:
    print(f"ℹ️ Policy already exists. Using existing ARN.")
    policy_arn = f"arn:aws:iam::263307268672:policy/{policy_name}"  # Replace YOUR_ACCOUNT_ID
except Exception as e:
    print(f"❌ Failed to create policy: {e}")
    exit(1)

# Attach to role
try:
    print(f"🔗 Attaching policy to role: {role_name}")
    iam.attach_role_policy(RoleName=role_name, PolicyArn=policy_arn)
    print("✅ Policy attached successfully.")
except Exception as e:
    print(f"❌ Failed to attach policy: {e}")
