import boto3
import sys
import json

def add_spa_redirect(distribution_id):
    client = boto3.client('cloudfront')

    # Step 1: Fetch current config and ETag
    try:
        response = client.get_distribution_config(Id=distribution_id)
        config = response['DistributionConfig']
        etag = response['ETag']
        print(f"✅ Retrieved config for distribution: {distribution_id}")
    except Exception as e:
        print(f"❌ Failed to get distribution config: {e}")
        sys.exit(1)

    # Step 2: Backup current config
    backup_file = f"cloudfront_spa_backup_{distribution_id}.json"
    with open(backup_file, "w") as f:
        json.dump(config, f, indent=2)
        print(f"📦 Backup saved to {backup_file}")

    # Step 3: Add or update custom error response for 404 → /index.html
    existing_errors = config.get("CustomErrorResponses", {}).get("Items", [])
    error_already_set = any(
        e.get("ErrorCode") == 404 and e.get("ResponsePagePath") == "/index.html"
        for e in existing_errors
    )

    if error_already_set:
        print("⚠️ Custom error response for 404 → /index.html already exists. No changes made.")
        return

    # Add new error response
    new_error = {
        "ErrorCode": 404,
        "ResponsePagePath": "/index.html",
        "ResponseCode": "200",
        "ErrorCachingMinTTL": 0
    }

    updated_errors = existing_errors + [new_error]
    config["CustomErrorResponses"] = {
        "Quantity": len(updated_errors),
        "Items": updated_errors
    }

    # Step 4: Update distribution
    try:
        result = client.update_distribution(
            Id=distribution_id,
            IfMatch=etag,
            DistributionConfig=config
        )
        print("✅ Custom error response added: 404 → /index.html with 200 OK.")
    except Exception as e:
        print(f"❌ Failed to update distribution: {e}")
        sys.exit(1)

# ---- Entry Point ----

if __name__ == "__main__":
    DISTRIBUTION_ID = "E122V50REJOK3C"

    if DISTRIBUTION_ID == "YOUR_DISTRIBUTION_ID":
        print("❌ Please set DISTRIBUTION_ID in the script.")
        sys.exit(1)

    add_spa_redirect(DISTRIBUTION_ID)
