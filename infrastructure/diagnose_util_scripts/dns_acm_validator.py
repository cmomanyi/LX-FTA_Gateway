import boto3
import socket
import dns.resolver
import time

# CONFIG
DOMAIN = "portal.lx-gateway.tech"
ZONE_NAME = "lx-gateway.tech"
EXPECTED_NS = {
    "ns-1670.awsdns-16.co.uk.",
    "ns-961.awsdns-56.net.",
    "ns-359.awsdns-44.com.",
    "ns-1413.awsdns-48.org."
}
CERT_ARN = "arn:aws:acm:us-east-1:263307268672:certificate/3e017cdc-f90a-41be-9c85-72e264d34cd2"


def check_ns_records():
    print(f"\n🔍 Checking NS records for {ZONE_NAME}...")
    try:
        answers = dns.resolver.resolve(ZONE_NAME, "NS")
        ns_records = {str(r).lower().strip('.') + '.' for r in answers}
        print(f"🔎 Found NS records: {ns_records}")
        if ns_records == EXPECTED_NS:
            print("✅ NS records match expected Route 53 values.")
        else:
            print("❌ NS records do not match Route 53. Check your domain registrar.")
    except Exception as e:
        print(f"❌ Failed to resolve NS: {e}")


def check_a_record():
    print(f"\n🔍 Checking A record for {DOMAIN}...")
    try:
        ip = socket.gethostbyname(DOMAIN)
        print(f"✅ A record found. IP: {ip}")
    except Exception as e:
        print(f"⚠️ A record not found for {DOMAIN}: {e}")


def check_acm_status():
    print(f"\n🔍 Checking ACM Certificate status for {CERT_ARN}...")
    acm = boto3.client("acm", region_name="us-east-1")
    try:
        response = acm.describe_certificate(CertificateArn=CERT_ARN)
        status = response["Certificate"]["Status"]
        print(f"✅ ACM Certificate Status: {status}")
        if status != "ISSUED":
            print("⚠️ Certificate is not yet issued. Check validation records.")
    except Exception as e:
        print(f"❌ Error checking certificate: {e}")


if __name__ == "__main__":
    print("🔎 Starting DNS + ACM Checks...")
    check_ns_records()
    check_a_record()
    check_acm_status()
