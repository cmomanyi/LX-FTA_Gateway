import subprocess
import boto3

# Configuration
domain_name = "portal.lx-gateway.tech"
hosted_zone_name = "lx-gateway.tech"
record_type = "A"
resource_name = "aws_route53_record.frontend_alias"


def get_hosted_zone_id(domain):
    client = boto3.client("route53")
    zones = client.list_hosted_zones_by_name(DNSName=domain, MaxItems="1")
    if zones["HostedZones"]:
        return zones["HostedZones"][0]["Id"].split("/")[-1]
    else:
        raise Exception(f"No hosted zone found for domain: {domain}")


def import_record():
    try:
        print(f"🔍 Fetching hosted zone ID for {hosted_zone_name}...")
        zone_id = get_hosted_zone_id(hosted_zone_name)
        print(f"✅ Found Zone ID: {zone_id}")

        import_id = f"{zone_id}_{domain_name}_{record_type}"
        print(f"🚀 Importing Route53 A record to Terraform: {resource_name}...")
        result = subprocess.run(
            ["terraform", "import", resource_name, import_id],
            check=True,
            capture_output=True,
            text=True
        )
        print(f"✅ Terraform import completed:\n{result.stdout}")

    except subprocess.CalledProcessError as e:
        print(f"❌ Terraform import failed:\n{e.stderr}")
    except Exception as err:
        print(f"❌ Error occurred: {err}")


if __name__ == "__main__":
    import_record()
