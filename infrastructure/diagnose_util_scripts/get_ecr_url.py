import boto3


def get_ecr_registry_url(region="us-east-1"):
    # Initialize STS and ECR clients
    sts_client = boto3.client("sts", region_name=region)
    ecr_client = boto3.client("ecr", region_name=region)

    # Get AWS account ID
    account_id = sts_client.get_caller_identity()["Account"]

    # Construct ECR URL
    registry_url = f"{account_id}.dkr.ecr.{region}.amazonaws.com"

    print(f"✅ ECR Registry URL: {registry_url}")
    return registry_url


if __name__ == "__main__":
    get_ecr_registry_url()
