import boto3
import subprocess
import sys
from botocore.exceptions import NoCredentialsError

# Set repository name
repository_name = "lx-fta_gateway-backend"


def aws_login():
    """Prompt user for AWS credentials and create a session."""
    print("🔐 AWS Login")
    access_key = input("Enter your AWS Access Key ID: ").strip()
    secret_key = input("Enter your AWS Secret Access Key: ").strip()
    region = input("Enter your AWS Region (e.g., us-east-1): ").strip()

    try:
        session = boto3.Session(
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
        # Test session
        sts = session.client("sts")
        account_id = sts.get_caller_identity()["Account"]
        print(f"✅ Logged into AWS as Account ID: {account_id}")
        return session
    except NoCredentialsError:
        print("❌ Invalid AWS credentials")
        sys.exit(1)
    except Exception as e:
        print("❌ Error during AWS login:", e)
        sys.exit(1)


def get_ecr_registry_uri(session):
    """Construct the ECR registry URI using the session credentials."""
    sts = session.client("sts")
    account_id = sts.get_caller_identity()["Account"]
    region = session.region_name
    return f"{account_id}.dkr.ecr.{region}.amazonaws.com"


def create_ecr_repository(session, repo_name):
    """Create ECR repository if it doesn't already exist."""
    client = session.client("ecr")
    try:
        client.create_repository(repositoryName=repo_name)
        print(f"📦 Repository '{repo_name}' created.")
    except client.exceptions.RepositoryAlreadyExistsException:
        print(f"ℹ️ Repository '{repo_name}' already exists.")
    except Exception as e:
        print("❌ Error creating repository:", str(e))
        sys.exit(1)


def authenticate_docker(ecr_url, session):
    """Authenticate Docker with AWS ECR using session credentials."""
    try:
        print("🔑 Authenticating Docker with ECR...")
        ecr = session.client("ecr")
        password = ecr.get_authorization_token()["authorizationData"][0]["authorizationToken"]
        docker_login_cmd = [
            "docker", "login",
            "--username", "AWS",
            "--password", password,
            ecr_url
        ]
        subprocess.run(docker_login_cmd, check=True)
        print("✅ Docker authenticated successfully.")
    except Exception as e:
        print("❌ Docker login failed:", str(e))
        sys.exit(1)


def build_and_push_docker_image(ecr_url, repo_name):
    """Build, tag, and push Docker image to ECR."""
    try:
        print("🐳 Building Docker image...")
        subprocess.run(["docker", "build", "-t", repo_name, "."], check=True)

        image_tag = f"{ecr_url}/{repo_name}:latest"
        print(f"🏷️ Tagging image as {image_tag}...")
        subprocess.run(["docker", "tag", f"{repo_name}:latest", image_tag], check=True)

        print("🚀 Pushing image to ECR...")
        subprocess.run(["docker", "push", image_tag], check=True)
        print("✅ Image pushed successfully.")
    except subprocess.CalledProcessError as e:
        print("❌ Docker command failed:", e)
        sys.exit(1)


if __name__ == "__main__":
    session = aws_login()
    ecr_url = get_ecr_registry_uri(session)
    print(f"📍 ECR Registry URI: {ecr_url}")
    create_ecr_repository(session, repository_name)
    authenticate_docker(ecr_url, session)
    build_and_push_docker_image(ecr_url, repository_name)
