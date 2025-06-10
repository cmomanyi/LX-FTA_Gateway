import boto3
import json

# Configuration
ROLE_NAME = "GitHubActionsDeployRole"
POLICY_NAME = "FullInfraDeployPolicy"
BUCKET_NAME = "lx-fta-frontend"
ECR_REPO_NAME = "lx-fta-backend"
CLUSTER_NAME = "lx-fta-cluster"
DYNAMODB_TABLE = "lx_fta_audit_logs"
REGION = "us-east-1"
ACCOUNT_ID = "263307268672"

policy_document = {
    "Version": "2012-10-17",
    "Statement": [
        # S3 Website Hosting
        {
            "Sid": "S3WebsiteConfig",
            "Effect": "Allow",
            "Action": [
                "s3:PutBucketWebsite",
                "s3:GetBucketWebsite"
            ],
            "Resource": f"arn:aws:s3:::{BUCKET_NAME}"
        },
        # S3 Public Access Block
        {
            "Sid": "S3PublicAccess",
            "Effect": "Allow",
            "Action": [
                "s3:PutBucketPublicAccessBlock",
                "s3:GetBucketPublicAccessBlock"
            ],
            "Resource": f"arn:aws:s3:::{BUCKET_NAME}"
        },
        # S3 Bucket Policy
        {
            "Sid": "S3BucketPolicy",
            "Effect": "Allow",
            "Action": [
                "s3:PutBucketPolicy",
                "s3:GetBucketPolicy"
            ],
            "Resource": f"arn:aws:s3:::{BUCKET_NAME}"
        },
        # S3 Object Access
        {
            "Sid": "S3ObjectCRUD",
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject"
            ],
            "Resource": f"arn:aws:s3:::{BUCKET_NAME}/*"
        },
        # S3 List + GetBucketLocation
        {
            "Sid": "S3ListAndLocation",
            "Effect": "Allow",
            "Action": [
                "s3:ListBucket",
                "s3:GetBucketLocation"
            ],
            "Resource": f"arn:aws:s3:::{BUCKET_NAME}"
        },
        # CloudFront Invalidation & Tagging
        {
            "Sid": "CloudFrontInvalidate",
            "Effect": "Allow",
            "Action": [
                "cloudfront:CreateInvalidation",
                "cloudfront:TagResource"
            ],
            "Resource": "*"
        },
        # ECR Auth + Push/Pull
        {
            "Sid": "ECRAuth",
            "Effect": "Allow",
            "Action": [
                "ecr:GetAuthorizationToken"
            ],
            "Resource": "*"
        },
        {
            "Sid": "ECRPushPull",
            "Effect": "Allow",
            "Action": [
                "ecr:BatchCheckLayerAvailability",
                "ecr:GetDownloadUrlForLayer",
                "ecr:BatchGetImage",
                "ecr:PutImage",
                "ecr:InitiateLayerUpload",
                "ecr:UploadLayerPart",
                "ecr:CompleteLayerUpload"
            ],
            "Resource": f"arn:aws:ecr:{REGION}:{ACCOUNT_ID}:repository/{ECR_REPO_NAME}"
        },
        {
            "Sid": "ECRDescribe",
            "Effect": "Allow",
            "Action": [
                "ecr:DescribeRepositories"
            ],
            "Resource": f"arn:aws:ecr:{REGION}:{ACCOUNT_ID}:repository/{ECR_REPO_NAME}"
        },
        # ECS Cluster Describe
        {
            "Sid": "ECSDescribe",
            "Effect": "Allow",
            "Action": [
                "ecs:DescribeClusters"
            ],
            "Resource": f"arn:aws:ecs:{REGION}:{ACCOUNT_ID}:cluster/{CLUSTER_NAME}"
        },
        # CloudWatch Logs
        {
            "Sid": "CloudWatchDescribe",
            "Effect": "Allow",
            "Action": [
                "logs:DescribeLogGroups"
            ],
            "Resource": "*"
        },
        # IAM Role Fetch
        {
            "Sid": "IAMGetRole",
            "Effect": "Allow",
            "Action": [
                "iam:GetRole"
            ],
            "Resource": f"arn:aws:iam::{ACCOUNT_ID}:role/ecsTaskExecutionRole"
        },
        # EC2 Describe SGs
        {
            "Sid": "EC2DescribeSG",
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeSecurityGroups"
            ],
            "Resource": "*"
        },
        # ELBv2 Describe Target Groups
        {
            "Sid": "ELBDescribeTG",
            "Effect": "Allow",
            "Action": [
                "elasticloadbalancing:DescribeTargetGroups"
            ],
            "Resource": "*"
        },
        # DynamoDB Describe
        {
            "Sid": "DynamoDBDescribe",
            "Effect": "Allow",
            "Action": [
                "dynamodb:DescribeTable"
            ],
            "Resource": f"arn:aws:dynamodb:{REGION}:{ACCOUNT_ID}:table/{DYNAMODB_TABLE}"
        }
    ]
}

def attach_inline_policy():
    iam = boto3.client("iam", region_name=REGION)
    try:
        iam.put_role_policy(
            RoleName=ROLE_NAME,
            PolicyName=POLICY_NAME,
            PolicyDocument=json.dumps(policy_document)
        )
        print(f"✅ IAM policy '{POLICY_NAME}' successfully attached to role '{ROLE_NAME}'.")
    except Exception as e:
        print(f"❌ Failed to attach policy: {e}")

if __name__ == "__main__":
    attach_inline_policy()
