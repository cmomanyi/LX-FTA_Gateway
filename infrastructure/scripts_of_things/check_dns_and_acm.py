import boto3
import dns.resolver
import sys

# ---------- CONFIGURATION ----------
DOMAIN = "lx-gateway.tech"
SUBDOMAIN = "portal.lx-gateway.tech"
EXPECTED_NS = {
    "ns-799.awsdns-35.net.",
    "ns-98.awsdns-12.com.",
    "ns-1826.awsdns-36.co.uk.",
    "ns-1482.awsdns-57.org.",
}
REGION = "us-east-1"
# Replace this with your actual ACM Certificate ARN
CERT_ARN = "arn:aws:acm:us-east-1:263307268672:certificate/3e017cdc-f90a-41be-9c85-72e264d34cd2"


# ----------------------------------

def check_ns_records():
    try:
        print(f"🔍 Checking NS records for {DOMAIN}...")
        answers = dns.resolver.resolve(DOMAIN, 'NS')
        current_ns = {str(rdata).strip('.').lower() + '.' for rdata in answers}
        if current_ns == EXPECTED_NS:
            print("✅ NS records match expected AWS Route 53 values.\n")
        else:
            print("⚠️ NS records do NOT match.")
            print("    Current: ", current_ns)
            print("    Expected:", EXPECTED_NS, "\n")
    except Exception as e:
        print(f"❌ Failed to resolve NS: {e}\n")


def check_a_record():
    try:
        print(f"🔍 Checking A record for {SUBDOMAIN}...")
        answers = dns.resolver.resolve(SUBDOMAIN, 'A')
        print(f"✅ A record found: {[str(rdata) for rdata in answers]}\n")
    except Exception as e:
        print(f"⚠️ A record not found for {SUBDOMAIN}: {e}\n")


def check_acm_status():
    try:
        print(f"🔍 Checking ACM Certificate status for {CERT_ARN}...")
        client = boto3.client('acm', region_name=REGION)
        response = client.describe_certificate(CertificateArn=CERT_ARN)
        status = response['Certificate']['Status']
        print(f"✅ ACM Certificate Status: {status}\n")
    except Exception as e:
        print(f"❌ Failed to fetch ACM certificate status: {e}\n")


if __name__ == "__main__":
    print("🔎 Starting DNS + ACM Checks...\n")
    check_ns_records()
    check_a_record()
    check_acm_status()
