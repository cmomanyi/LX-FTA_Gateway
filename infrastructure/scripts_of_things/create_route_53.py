import boto3
from botocore.exceptions import ClientError

def create_public_hosted_zone(domain_name, caller_reference=None):
    route53 = boto3.client('route53')

    if caller_reference is None:
        import uuid
        caller_reference = str(uuid.uuid4())  # Unique ID for this request

    try:
        response = route53.create_hosted_zone(
            Name=domain_name,
            CallerReference=caller_reference,
            HostedZoneConfig={
                'Comment': f'Public hosted zone for {domain_name}',
                'PrivateZone': False
            }
        )

        zone_id = response['HostedZone']['Id']
        name_servers = response['DelegationSet']['NameServers']

        print(f"✅ Successfully created public hosted zone for '{domain_name}'")
        print(f"🆔 Hosted Zone ID: {zone_id}")
        print("🧭 Name servers:")
        for ns in name_servers:
            print(f" - {ns}")

        return response

    except ClientError as e:
        print(f"❌ Failed to create hosted zone: {e.response['Error']['Message']}")
        return None

# Run the creation
if __name__ == "__main__":
    create_public_hosted_zone("lx-gateway.tech")
