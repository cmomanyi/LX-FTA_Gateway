import boto3
import sys

# ----------- CONFIGURE THIS ----------- #
domain_name = "portal.lx-gateway.tech"   # Your domain
region = "us-east-1"                     # ACM region for CloudFront
# -------------------------------------- #

acm = boto3.client("acm", region_name=region)

def find_matching_cert(domain):
    paginator = acm.get_paginator('list_certificates')
    for page in paginator.paginate(CertificateStatuses=['ISSUED']):
        for cert in page['CertificateSummaryList']:
            if cert['DomainName'] == domain:
                return cert['CertificateArn']
    return None

def validate_certificate(cert_arn):
    try:
        response = acm.describe_certificate(CertificateArn=cert_arn)
        cert = response['Certificate']
        print(f"\n✅ Found certificate for: {cert['DomainName']}")
        print(f"   - Status: {cert['Status']}")
        print(f"   - In Use: {'Yes' if cert.get('InUseBy') else 'No'}")
        print(f"   - Issuer: {cert.get('Issuer')}")
        print(f"   - Type: {cert.get('Type')}")
        print(f"   - ARN: {cert['CertificateArn']}")
        if cert['Status'] != 'ISSUED':
            print("❌ Certificate exists but is not ISSUED.")
        else:
            print("✅ Certificate is valid and ready for CloudFront.")
    except Exception as e:
        print(f"❌ Error describing certificate: {e}")

def request_new_certificate(domain):
    print(f"Requesting a new certificate for {domain}...")
    try:
        response = acm.request_certificate(
            DomainName=domain,
            ValidationMethod='DNS',
            IdempotencyToken='cloudfront-cert',
            Options={'CertificateTransparencyLoggingPreference': 'ENABLED'}
        )
        print(f"✅ Certificate requested. ARN: {response['CertificateArn']}")
    except Exception as e:
        print(f"❌ Failed to request new certificate: {e}")

if __name__ == "__main__":
    cert_arn = find_matching_cert(domain_name)

    if cert_arn:
        validate_certificate(cert_arn)
    else:
        print(f"❌ No issued certificate found for {domain_name}.")
        # Uncomment this line to auto-request one if missing:
        # request_new_certificate(domain_name)
