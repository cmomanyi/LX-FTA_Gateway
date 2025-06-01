import docker
import subprocess
import os
import sys

# Configuration
AWS_ACCOUNT_ID = "263307268672"
AWS_REGION = "us-east-1"
REPO_NAME = "lx-fta-backend"
TAG = "latest"

DOCKERFILE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")

print(f"📁 Building Docker image from: {DOCKERFILE_DIR}")

ECR_URL = f"{AWS_ACCOUNT_ID}.dkr.ecr.{AWS_REGION}.amazonaws.com/{REPO_NAME}"


def run_command(cmd):
    print(f"📦 Running: {cmd}")
    result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
    return result.stdout.strip()


def docker_login_ecr():
    print("🔐 Logging in to ECR...")
    login_cmd = f"aws ecr get-login-password --region {AWS_REGION} | docker login --username AWS --password-stdin {AWS_ACCOUNT_ID}.dkr.ecr.{AWS_REGION}.amazonaws.com"
    run_command(login_cmd)


def build_image():
    print(f"📁 Dockerfile path: {DOCKERFILE_DIR}")
    print("📦 Files:", os.listdir(DOCKERFILE_DIR))

    client = docker.from_env()
    image, logs = client.images.build(
        path=DOCKERFILE_DIR,
        tag=f"{REPO_NAME}:{TAG}",
        dockerfile="Dockerfile"  # explicitly declare it
    )
    for chunk in logs:
        if "stream" in chunk:
            print(chunk["stream"].strip())
    print("✅ Docker image built successfully.")

    return image


def tag_and_push_image(image):
    print(f"🏷️ Tagging image for ECR: {ECR_URL}:{TAG}")
    image.tag(ECR_URL, tag=TAG)

    print(f"📤 Pushing image to ECR: {ECR_URL}:{TAG}")
    client = docker.from_env()
    for line in client.images.push(ECR_URL, tag=TAG, stream=True, decode=True):
        if 'status' in line:
            print(line['status'])


def test_container():
    print("🧪 Running container for test (http://localhost:8000)...")
    client = docker.from_env()
    try:
        container = client.containers.run(f"{REPO_NAME}:{TAG}", ports={'8000/tcp': 8000}, detach=True)
        print(f"✅ Container {container.short_id} is running. CTRL+C to stop.")
    except Exception as e:
        print(f"❌ Error running container: {e}")


if __name__ == "__main__":
    try:
        docker_login_ecr()
        image = build_image()
        tag_and_push_image(image)
        test_container()  # Comment this out for CI/CD
    except subprocess.CalledProcessError as e:
        print("❌ Shell command failed:")
        print(e.stderr)
        sys.exit(1)
