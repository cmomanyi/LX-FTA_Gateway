import boto3
import json

# Replace with your actual values
bucket_name = "lx-fta-frontend"
cloudfront_dist_id = "E1R5RPWCTLLS09"  # Replace with your actual CloudFront distribution ID
aws_account_id = "263307268672"

# Policy to allow CloudFront to read objects from the S3 bucket
policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowCloudFrontServicePrincipalReadOnly",
            "Effect": "Allow",
            "Principal": {
                "Service": "cloudfront.amazonaws.com"
            },
            "Action": "s3:GetObject",
            "Resource": f"arn:aws:s3:::{bucket_name}/*",
            "Condition": {
                "StringEquals": {
                    "AWS:SourceArn": f"arn:aws:cloudfront::{aws_account_id}:distribution/{cloudfront_dist_id}"
                }
            }
        }
    ]
}

# Attach policy to the bucket
s3 = boto3.client("s3")
s3.put_bucket_policy(
    Bucket=bucket_name,
    Policy=json.dumps(policy)
)

print(f"✅ Policy attached to S3 bucket {bucket_name} to allow CloudFront access.")
