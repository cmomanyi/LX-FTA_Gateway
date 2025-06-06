import json
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client('s3')

def lambda_handler(event, context):
    bucket = 'your-bucket-name'
    uuid = 'your-uuid-prefix-value'
    batch = 'your-batch-id'  # Optional, depending on your use

    resp = s3.list_objects_v2(Bucket=bucket)

    if 'Contents' in resp:
        for obj in resp['Contents']:
            key = obj['Key']
            print(key)
            print(key[0:36])

            if key.endswith('.json'):
                logger.info(f"Processing JSON file: '{key}'")

                try:
                    # Read file from S3
                    json_obj = s3.get_object(Bucket=bucket, Key=key)
                    content = json_obj['Body'].read().decode('utf-8')
                    data = json.loads(content)

                    # Extract veteran info
                    veteran = data.get("veteran", {})
                    vet_name = veteran.get("full_name", {})
                    vet_info = {
                        "first_name": vet_name.get("first", "N/A"),
                        "last_name": vet_name.get("last", "N/A"),
                        "dob": veteran.get("dob", "N/A")
                    }

                    # Extract applicant info
                    applicants = data.get("applicants", [])
                    applicant_info = []
                    for applicant in applicants:
                        name = applicant.get("applicantsname", {})
                        address = applicant.get("applicants address", {})
                        applicant_info.append({
                            "first": name.get("first", "N/A"),
                            "last": name.get("last", "N/A"),
                            "dob": applicant.get("applicant_dob", "N/A"),
                            "state": address.get("State", "N/A")
                        })

                    # Combine and log
                    processed_data = {
                        "veteran": vet_info,
                        "applicants": applicant_info
                    }
                    logger.info(f"Processed data from '{key}': {json.dumps(processed_data)}")

                except Exception as e:
                    logger.error(f"Error processing '{key}': {e}")

            else:
                # Check if the key matches the UUID prefix
                if key[0:36] == uuid:
                    try:
                        status = process_records(key, batch)
                        logger.info(f"Processed record with key '{key}', status: {status}")
                    except Exception as e:
                        logger.error(f"Error processing record '{key}': {e}")
    else:
        logger.info(f"No objects found in bucket '{bucket}'.")
