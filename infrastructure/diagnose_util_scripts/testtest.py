import requests
import sys

# Replace this with your actual ALB DNS name
ALB_DNS = "http://ecs-alb-99933138.us-east-1.elb.amazonaws.com"


def check_health():
    try:
        url = f"{ALB_DNS}/health"
        print(f"🔍 Checking health endpoint: {url}")
        response = requests.get(url, timeout=5)

        if response.status_code == 200:
            print("✅ FastAPI backend is healthy.")
            print("🩺 Response:", response.text)
        else:
            print(f"⚠️ Health check failed. Status: {response.status_code}")
            print("Response:", response.text)
    except requests.RequestException as e:
        print("❌ Error connecting to FastAPI backend:", str(e))
        sys.exit(1)


if __name__ == "__main__":
    check_health()
