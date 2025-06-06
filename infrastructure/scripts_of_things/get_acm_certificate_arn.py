import boto3

# Replace with your actual domain
TARGET_DOMAIN = "portal.lx-gateway.tech"
REGION = "us-east-1"


def get_certificate_arn(domain_name, region):
    client = boto3.client("acm", region_name=region)
    paginator = client.get_paginator("list_certificates")
    for page in paginator.paginate(CertificateStatuses=['PENDING_VALIDATION', 'ISSUED']):
        for cert in page["CertificateSummaryList"]:
            if cert["DomainName"] == domain_name:
                return cert["CertificateArn"]
    return None


if __name__ == "__main__":
    arn = get_certificate_arn(TARGET_DOMAIN, REGION)
    if arn:
        print(f"\n✅ Certificate ARN for {TARGET_DOMAIN}:\n{arn}")
    else:
        print(f"\n❌ No certificate found for domain: {TARGET_DOMAIN}")
