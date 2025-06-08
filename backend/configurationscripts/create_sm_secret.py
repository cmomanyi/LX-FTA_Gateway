import boto3
import json
from botocore.exceptions import ClientError

# Initialize Secrets Manager client
client = boto3.client("secretsmanager", region_name="us-east-1")  # Change region if needed

# Define secret name and payload
secret_name = "fta-user-auth-secrets"
secret_payload = {
    "admin": {"password": "admin123", "role": "admin"},
    "analyst": {"password": "analyst123", "role": "analyst"},
    "sensor": {"password": "sensor123", "role": "sensor"},
    "jwt_secret": "super_secure_quantum_key"
}

try:
    response = client.create_secret(
        Name=secret_name,
        Description="JWT key and user credentials for LX-FTA backend",
        SecretString=json.dumps(secret_payload)
    )
    print(f"✅ Secret created: {response['ARN']}")
except ClientError as e:
    if e.response['Error']['Code'] == 'ResourceExistsException':
        print(f"⚠️ Secret '{secret_name}' already exists. Updating instead...")

        update_response = client.put_secret_value(
            SecretId=secret_name,
            SecretString=json.dumps(secret_payload)
        )
        print(f"🔄 Secret updated: {update_response['ARN']}")
    else:
        raise
