import subprocess
import sys

# === Configuration ===
aws_account_id = "263307268672"
region = "us-east-1"
repository_name = "lx-fta-backend"
image_tag = "latest"
ecr_url = f"{aws_account_id}.dkr.ecr.{region}.amazonaws.com"
print(f"ecr_url: {ecr_url}")
full_image_name = f"{ecr_url}/{repository_name}:{image_tag}"
print(f"full_image_name: {full_image_name}")


def run_command(cmd, input_text=None):
    print(f"➡️ Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(
            cmd,
            input=input_text,
            text=True,
            check=True,
            capture_output=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {' '.join(cmd)}\n{e.stderr or e}")
        sys.exit(1)


def create_repository():
    print(f"📦 Creating ECR repository: {repository_name}")
    run_command([
        "aws", "ecr", "create-repository",
        "--repository-name", repository_name,
        "--region", region
    ])
    print("✅ Repository created (or already exists)")


def login_to_ecr():
    print("🔐 Logging in to ECR securely...")
    password = run_command(["aws", "ecr", "get-login-password", "--region", region])
    run_command(["docker", "login", "--username", "AWS", "--password-stdin", ecr_url], input_text=password)
    print("✅ Docker login succeeded")


def build_and_push_image():
    print(f"🔧 Building Docker image: {repository_name}")
    run_command(["docker", "build", "-t", repository_name, "."])

    print(f"🏷️ Tagging image as: {full_image_name}")
    run_command(["docker", "tag", f"{repository_name}:latest", full_image_name])

    print(f"🚀 Pushing image to ECR: {full_image_name}")
    run_command(["docker", "push", full_image_name])
    print("✅ Docker image pushed to ECR")


if __name__ == "__main__":
    create_repository()
    login_to_ecr()
    build_and_push_image()
