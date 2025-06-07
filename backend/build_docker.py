# build_docker.py

import subprocess

# Configuration
image_name = "lx-fta-backend"
tag = "latest"
ecr_url = "<your-account-id>.dkr.ecr.us-east-1.amazonaws.com"  # Update with your actual account
full_image_name = f"{ecr_url}/{image_name}:{tag}"


def run_cmd(command):
    print(f"\n🔧 Running: {command}")
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        raise Exception(f"❌ Command failed: {command}")


def build_image():
    print("📦 Building Docker image...")
    run_cmd(f"docker build -t {image_name}:{tag} backend/")


def tag_image():
    print("🏷️ Tagging image...")
    run_cmd(f"docker tag {image_name}:{tag} {full_image_name}")


def push_image():
    print("🚀 Logging into ECR...")
    run_cmd(f"aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin {ecr_url}")

    print("📤 Pushing image to ECR...")
    run_cmd(f"docker push {full_image_name}")


def main():
    build_image()
    tag_image()
    push_image()
    print("\n✅ Docker image built and pushed successfully!")


if __name__ == "__main__":
    main()
