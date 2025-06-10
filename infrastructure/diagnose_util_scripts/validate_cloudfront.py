import boto3

# --- CONFIGURE THIS ---
domain_name = "portal.lx-gateway.tech"
region = "us-east-1"
hosted_zone_id = "ZXXXXXXXXXXXXXX"  # Replace with your actual Hosted Zone ID
# -----------------------

cf = boto3.client("cloudfront", region_name=region)
r53 = boto3.client("route53")

def find_cloudfront_distribution_for_alias(alias):
    paginator = cf.get_paginator("list_distributions")
    for page in paginator.paginate():
        for dist in page["DistributionList"].get("Items", []):
            if alias in dist["Aliases"].get("Items", []):
                return dist
    return None

def check_route53_record():
    try:
        response = r53.list_resource_record_sets(
            HostedZoneId=hosted_zone_id,
            StartRecordName=domain_name,
            StartRecordType='A',
            MaxItems='1'
        )
        record = response['ResourceRecordSets'][0]
        if record['Name'].rstrip('.') == domain_name and 'AliasTarget' in record:
            print(f"✅ Route53 A record found for {domain_name}")
            print(f"   → Alias points to: {record['AliasTarget']['DNSName']}")
            return record['AliasTarget']['DNSName']
        else:
            print(f"❌ No A record found for {domain_name}")
    except Exception as e:
        print(f"❌ Error querying Route53: {e}")
    return None

def validate():
    print(f"🔍 Checking CloudFront distribution for {domain_name}...")
    dist = find_cloudfront_distribution_for_alias(domain_name)
    if not dist:
        print(f"❌ No CloudFront distribution found with alias: {domain_name}")
        return

    cf_domain = dist["DomainName"]
    status = dist["Status"]
    cert_arn = dist["ViewerCertificate"]["ACMCertificateArn"]

    print(f"✅ CloudFront distribution found: {cf_domain}")
    print(f"   - Status: {status}")
    print(f"   - Certificate ARN: {cert_arn}")

    dns_target = check_route53_record()
    if dns_target and cf_domain in dns_target:
        print(f"✅ Route53 is correctly pointing to CloudFront")
    else:
        print(f"❌ Route53 is NOT pointing to the expected CloudFront domain")

if __name__ == "__main__":
    validate()
