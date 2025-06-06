import boto3
import time

domain = "portal.lx-gateway.tech"


def check_certificate(domain):
    client = boto3.client("acm", region_name="us-east-1")
    certs = client.list_certificates(CertificateStatuses=["PENDING_VALIDATION", "ISSUED"])
    cert_arn = None

    for cert in certs["CertificateSummaryList"]:
        if cert["DomainName"] == domain:
            cert_arn = cert["CertificateArn"]
            break

    if not cert_arn:
        print(f"❌ Certificate for {domain} not found.")
        return

    cert_details = client.describe_certificate(CertificateArn=cert_arn)["Certificate"]
    status = cert_details["Status"]
    print(f"🔍 Certificate Status for {domain}: {status}")

    if status == "PENDING_VALIDATION":
        print("⚠️  DNS validation still pending. Ensure Route 53 record exists.")
    elif status == "ISSUED":
        print("✅ Certificate issued and valid.")
    else:
        print(f"⚠️  Certificate in unexpected state: {status}")


def check_dns_record(domain):
    route53 = boto3.client("route53")
    hosted_zones = route53.list_hosted_zones_by_name(DNSName="lx-gateway.tech")["HostedZones"]

    if not hosted_zones:
        print("❌ No hosted zone found for lx-gateway.tech")
        return

    zone_id = hosted_zones[0]["Id"].split("/")[-1]
    records = route53.list_resource_record_sets(HostedZoneId=zone_id)["ResourceRecordSets"]

    found = any(
        record for record in records if record["Name"].startswith(domain + ".") and record["Type"] in ["A", "CNAME"])
    if found:
        print(f"✅ DNS alias record found for {domain}")
    else:
        print(f"❌ DNS record for {domain} not found. Check Route 53 settings.")


if __name__ == "__main__":
    check_certificate(domain)
    check_dns_record(domain)
