import boto3

def check_public_hosted_zone(domain_name):
    client = boto3.client('route53')

    # List all hosted zones
    response = client.list_hosted_zones()
    hosted_zones = response['HostedZones']

    # Normalize domain name with trailing dot
    normalized_domain = domain_name if domain_name.endswith('.') else domain_name + '.'

    for zone in hosted_zones:
        if zone['Name'] == normalized_domain:
            if not zone['Config']['PrivateZone']:
                print(f"✅ Public hosted zone for '{domain_name}' exists. HostedZoneId: {zone['Id']}")
                return True
            else:
                print(f"⚠️ Hosted zone for '{domain_name}' exists, but it is a **private** zone.")
                return False

    print(f"❌ No hosted zone found for '{domain_name}'.")
    return False

# Run the check
if __name__ == "__main__":
    check_public_hosted_zone("lxfta.io")
