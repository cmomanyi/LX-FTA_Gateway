import boto3
import time

DOMAIN_NAMES = ["portal.lx-gateway.tech", "lx-gateway.tech"]
HOSTED_ZONE_NAME = "lx-gateway.tech"
TFVARS_PATH = "terraform.tfvars"

acm = boto3.client("acm", region_name="us-east-1")
route53 = boto3.client("route53")


def request_certificate(domains):
    response = acm.request_certificate(
        DomainName=domains[0],
        SubjectAlternativeNames=domains[1:],
        ValidationMethod="DNS",
        Options={
            "CertificateTransparencyLoggingPreference": "ENABLED"
        },
        IdempotencyToken="lxgateway",
        Tags=[{"Key": "Name", "Value": "lx-gateway-cert"}]
    )
    return response["CertificateArn"]


def get_validation_records(cert_arn):
    while True:
        cert = acm.describe_certificate(CertificateArn=cert_arn)
        options = cert["Certificate"]["DomainValidationOptions"]
        if all("ResourceRecord" in d for d in options):
            return options
        print("⏳ Waiting for ACM to generate DNS validation records...")
        time.sleep(5)


def find_hosted_zone_id(zone_name):
    zones = route53.list_hosted_zones_by_name(DNSName=zone_name)["HostedZones"]
    for zone in zones:
        if zone["Name"].rstrip(".") == zone_name:
            return zone["Id"].split("/")[-1]
    raise Exception(f"Hosted zone {zone_name} not found")


def create_route53_records(validation_options, hosted_zone_id):
    changes = []
    for option in validation_options:
        rr = option["ResourceRecord"]
        changes.append({
            "Action": "UPSERT",
            "ResourceRecordSet": {
                "Name": rr["Name"],
                "Type": rr["Type"],
                "TTL": 300,
                "ResourceRecords": [{"Value": rr["Value"]}]
            }
        })
    route53.change_resource_record_sets(
        HostedZoneId=hosted_zone_id,
        ChangeBatch={
            "Comment": "Add ACM validation CNAMEs",
            "Changes": changes
        }
    )


def wait_for_issuance(cert_arn):
    print("⏳ Waiting for certificate to be ISSUED...")
    while True:
        status = acm.describe_certificate(CertificateArn=cert_arn)["Certificate"]["Status"]
        print(f"🔍 Current status: {status}")
        if status == "ISSUED":
            print("✅ Certificate issued.")
            break
        elif status == "FAILED":
            raise Exception("❌ Certificate issuance failed.")
        time.sleep(10)


def update_tfvars(cert_arn, path):
    updated_lines = []
    found = False
    with open(path, "r") as file:
        for line in file:
            if line.strip().startswith("certificate_arn"):
                updated_lines.append(f'certificate_arn = "{cert_arn}"\n')
                found = True
            else:
                updated_lines.append(line)
    if not found:
        updated_lines.append(f'\ncertificate_arn = "{cert_arn}"\n')

    with open(path, "w") as file:
        file.writelines(updated_lines)

    print(f"📄 Updated {path} with new certificate ARN.")


if __name__ == "__main__":
    print("📌 Requesting ACM certificate...")
    cert_arn = request_certificate(DOMAIN_NAMES)

    print("🔍 Getting DNS validation records...")
    validation_options = get_validation_records(cert_arn)

    print("📬 Creating Route 53 DNS records...")
    hosted_zone_id = find_hosted_zone_id(HOSTED_ZONE_NAME)
    create_route53_records(validation_options, hosted_zone_id)

    wait_for_issuance(cert_arn)

    update_tfvars(cert_arn, TFVARS_PATH)
