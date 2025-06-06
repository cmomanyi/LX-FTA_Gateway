import boto3
import socket
import time

domain = "portal.lx-gateway.tech"
cert_arn = "arn:aws:acm:us-east-1:263307268672:certificate/3e017cdc-f90a-41be-9c85-72e264d34cd2"
region = "us-east-1"


def check_dns(domain):
    print(f"🔍 Checking DNS resolution for {domain}...")
    try:
        ip = socket.gethostbyname(domain)
        print(f"✅ DNS resolves to IP: {ip}")
    except socket.gaierror:
        print(f"⚠️ DNS resolution failed: The DNS query name does not exist: {domain}")


def check_acm_status(cert_arn):
    print(f"\n🔍 Checking ACM Certificate status for {cert_arn}...")
    acm = boto3.client('acm', region_name=region)
    response = acm.describe_certificate(CertificateArn=cert_arn)
    status = response['Certificate']['Status']
    print(f"📄 Status: {status}")
    if status == "ISSUED":
        print("✅ Certificate has been issued.")
    else:
        print("⚠️ Certificate not ready.")


if __name__ == "__main__":
    print("🔎 Starting DNS + ACM Checks...\n")
    check_dns(domain)
    check_acm_status(cert_arn)
