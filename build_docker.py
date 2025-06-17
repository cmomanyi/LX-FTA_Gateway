import boto3
import json

iam = boto3.client('iam')
role_name = "ecsTaskExecutionRole"

# ECS trust policy
trust_policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "ecs-tasks.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}

# Inline policy with necessary ECS permissions
execution_policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogStream",
                "logs:PutLogEvents",
                "ecr:GetAuthorizationToken",
                "ecr:BatchCheckLayerAvailability",
                "ecr:GetDownloadUrlForLayer",
                "ecr:BatchGetImage",
                "secretsmanager:GetSecretValue",
                "ssm:GetParameters"
            ],
            "Resource": "*"
        }
    ]
}

try:
    iam.get_role(RoleName=role_name)
    iam.update_assume_role_policy(
        RoleName=role_name,
        PolicyDocument=json.dumps(trust_policy)
    )
    print(f"✅ Updated trust relationship for role '{role_name}'.")
except iam.exceptions.NoSuchEntityException:
    iam.create_role(
        RoleName=role_name,
        AssumeRolePolicyDocument=json.dumps(trust_policy),
        Description="ECS Task Execution Role for Fargate"
    )
    print(f"✅ Created new role '{role_name}' with ECS trust policy.")

iam.put_role_policy(
    RoleName=role_name,
    PolicyName="AmazonECSTaskExecutionInlinePolicy",
    PolicyDocument=json.dumps(execution_policy)
)
print(f"✅ Attached ECS execution inline policy to role '{role_name}'.")
