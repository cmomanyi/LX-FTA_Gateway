import boto3
import json
import sys

def add_spa_redirect(distribution_id):
    client = boto3.client('cloudfront')

    # Step 1: Get current config
    try:
        response = client.get_distribution_config(Id=distribution_id)
        config = response['DistributionConfig']
        etag = response['ETag']
        print(f"✅ Retrieved distribution config for {distribution_id}")
    except Exception as e:
        print(f"❌ Failed to get distribution config: {e}")
        sys.exit(1)

    # Step 2: Backup existing config
    backup_file = f"cloudfront_backup_{distribution_id}.json"
    try:
        with open(backup_file, "w") as f:
            json.dump(config, f, indent=2)
        print(f"📦 Backup of config saved to {backup_file}")
    except Exception as e:
        print(f"❌ Failed to write backup file: {e}")
        sys.exit(1)

    # Step 3: Ensure ForwardedValues.Headers is valid (NO Upgrade/Connection)
    if 'DefaultCacheBehavior' in config:
        if 'ForwardedValues' in config['DefaultCacheBehavior']:
            config['DefaultCacheBehavior']['ForwardedValues']['Headers'] = {
                "Quantity": 0,
                "Items": []
            }

    # Step 4: Add 404 → /index.html redirect if not already present
    existing_errors = config.get("CustomErrorResponses", {}).get("Items", [])
    error_exists = any(
        e.get("ErrorCode") == 404 and e.get("ResponsePagePath") == "/index.html"
        for e in existing_errors
    )

    if not error_exists:
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
        print("🔁 Added custom 404 error response → /index.html")
    else:
        print("ℹ️ Custom 404 redirect already present. Skipping error response addition.")

    # Step 5: Update distribution
    try:
        client.update_distribution(
            Id=distribution_id,
            IfMatch=etag,
            DistributionConfig=config
        )
        print(f"✅ CloudFront distribution '{distribution_id}' updated for SPA routing support.")
    except Exception as e:
        print(f"❌ Failed to update distribution: {e}")
        sys.exit(1)

# ---- Entry Point ----
if __name__ == "__main__":
    DISTRIBUTION_ID = "E122V50REJOK3C"

    if DISTRIBUTION_ID == "YOUR_DISTRIBUTION_ID":
        print("❌ Please set DISTRIBUTION_ID before running.")
        sys.exit(1)

    add_spa_redirect(DISTRIBUTION_ID)





# ---------- Main Entry Point ----------
#
# if __name__ == "__main__":
#     # Replace these with your actual values
#     DISTRIBUTION_ID = "E122V50REJOK3C"
#     NEW_ORIGIN_DOMAIN = "api-alb-1736317623.us-east-1.elb.amazonaws.com"
#
#     if DISTRIBUTION_ID == "YOUR_DISTRIBUTION_ID" or "your-alb-name" in NEW_ORIGIN_DOMAIN:
#         print("❌ Please set DISTRIBUTION_ID and NEW_ORIGIN_DOMAIN before running.")
#         sys.exit(1)
#
#     enable_websockets(DISTRIBUTION_ID, NEW_ORIGIN_DOMAIN)
