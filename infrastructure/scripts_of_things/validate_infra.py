import boto3
import dns.resolver
from botocore.exceptions import ClientError

# ---------- CONFIGURATION ----------
REGION = "us-east-1"
CERT_ARN = "arn:aws:acm:us-east-1:263307268672:certificate/3e017cdc-f90a-41be-9c85-72e264d34cd2"
DOMAIN_NAME = "portal.lx-gateway.tech"


# -----------------------------------

def check_certificate_status():
    print("🔍 Checking ACM Certificate status...")
    acm = boto3.client("acm", region_name=REGION)
    try:
        response = acm.describe_certificate(CertificateArn=CERT_ARN)
        status = response['Certificate']['Status']
        print(f"✅ Certificate Status: {status}")
    except ClientError as e:
        print(f"❌ Failed to retrieve certificate: {e}")


def check_dns():
    print("\n🔍 Checking DNS resolution...")
    try:
        answers = dns.resolver.resolve(DOMAIN_NAME, 'A')
        print(f"✅ DNS Resolved: {[rdata.to_text() for rdata in answers]}")
    except Exception as e:
        print(f"⚠️ DNS resolution failed: {e}")


def check_cloudfront_status():
    print("\n🔍 Checking CloudFront Distributions...")
    cf = boto3.client("cloudfront", region_name=REGION)
    try:
        dists = cf.list_distributions()
        found = False
        for dist in dists['DistributionList'].get('Items', []):
            if DOMAIN_NAME in [alias['CNAME'] for alias in dist.get('Aliases', {}).get('Items', [])]:
                print(f"✅ CloudFront found for {DOMAIN_NAME}")
                print(f"    ID: {dist['Id']}")
                print(f"    Status: {dist['Status']}")
                print(f"    Domain: {dist['DomainName']}")
                found = True
        if not found:
            print("⚠️ No CloudFront distribution found for the domain.")
    except ClientError as e:
        print(f"❌ Failed to check CloudFront: {e}")


if __name__ == "__main__":
    print("🛠️ Validating LX-FTA Deployment...\n")
    check_certificate_status()
    check_dns()
    check_cloudfront_status()
