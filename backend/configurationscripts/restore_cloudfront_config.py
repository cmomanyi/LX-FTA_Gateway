import boto3
import json
import sys
import os


def restore_cloudfront_config(distribution_id, backup_file_path):
    client = boto3.client('cloudfront')

    # Step 1: Load the backup config
    if not os.path.exists(backup_file_path):
        print(f"❌ Backup file not found: {backup_file_path}")
        sys.exit(1)

    try:
        with open(backup_file_path, "r") as f:
            backup_config = json.load(f)
        print(f"📦 Loaded backup config from {backup_file_path}")
    except Exception as e:
        print(f"❌ Failed to load backup config: {e}")
        sys.exit(1)

    # Step 2: Get current ETag (required for update)
    try:
        response = client.get_distribution_config(Id=distribution_id)
        etag = response['ETag']
    except Exception as e:
        print(f"❌ Failed to fetch current distribution ETag: {e}")
        sys.exit(1)

    # Step 3: Restore distribution
    try:
        result = client.update_distribution(
            Id=distribution_id,
            IfMatch=etag,
            DistributionConfig=backup_config
        )
        print(f"✅ Successfully restored CloudFront distribution '{distribution_id}' from backup.")
    except Exception as e:
        print(f"❌ Failed to restore distribution: {e}")
        sys.exit(1)


# ---------- Main ----------

if __name__ == "__main__":
    # Set these values
    DISTRIBUTION_ID = "E122V50REJOK3C"
    BACKUP_FILE = f"cloudfront_backup_{DISTRIBUTION_ID}.json"

    if DISTRIBUTION_ID == "YOUR_DISTRIBUTION_ID":
        print("❌ Please set DISTRIBUTION_ID to the correct value.")
        sys.exit(1)

    restore_cloudfront_config(DISTRIBUTION_ID, BACKUP_FILE)
