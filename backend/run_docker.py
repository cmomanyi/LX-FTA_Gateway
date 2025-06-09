import boto3
import json
import logging
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# ---- Configuration ----
AWS_REGION = "us-east-1"
SECRET_ARN = "arn:aws:secretsmanager:us-east-1:263307268672:secret:lx-fta-auth-secrets-gTBwYG"

def fetch_auth_secrets():
    logging.info(f"Fetching secret from ARN: {SECRET_ARN} in region: {AWS_REGION}")

    try:
        client = boto3.client("secretsmanager", region_name=AWS_REGION)
        response = client.get_secret_value(SecretId=SECRET_ARN)

        secret_string = response.get("SecretString")
        if not secret_string:
            logging.error("SecretString not found in Secrets Manager response.")
            sys.exit(1)

        secrets = json.loads(secret_string)
        logging.info("Successfully fetched and parsed secrets.")
        return secrets

    except client.exceptions.ResourceNotFoundException:
        logging.error("The requested secret was not found.")
    except client.exceptions.InvalidRequestException as e:
        logging.error(f"Invalid request: {e}")
    except client.exceptions.InvalidParameterException as e:
        logging.error(f"Invalid parameter: {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")

    sys.exit(1)

# Run when the script is executed
if __name__ == "__main__":
    secrets = fetch_auth_secrets()
    print("\n✅ Secrets:")
    print(json.dumps(secrets, indent=2))
