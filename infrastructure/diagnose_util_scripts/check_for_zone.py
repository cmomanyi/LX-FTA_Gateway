import boto3
import os
import json
import logging

logging.basicConfig(level=logging.DEBUG)


def fetch_auth_secrets():
    secret_arn = os.getenv("SECRETSMANAGER_SECRET_ARN")
    region = os.getenv("AWS_REGION", "us-east-1")

    logging.debug(f"SECRETSMANAGER_SECRET_ARN: {secret_arn}")
    logging.debug(f"AWS_REGION: {region}")

    if not secret_arn:
        raise ValueError("❌ SECRETSMANAGER_SECRET_ARN is not set.")

    try:
        client = boto3.client("secretsmanager", region_name=region)
        response = client.get_secret_value(SecretId=secret_arn)

        logging.debug("✅ AWS SecretsManager response received.")
        logging.debug(f"Raw response: {response}")

        secret_string = response.get("SecretString")
        if not secret_string:
            raise ValueError("❌ SecretString is missing in the response.")

        secrets = json.loads(secret_string)
        logging.debug(f"✅ Parsed secrets: {secrets}")
        return secrets

    except Exception as e:
        logging.error(f"❌ Failed to fetch or parse secrets: {e}")
        raise
