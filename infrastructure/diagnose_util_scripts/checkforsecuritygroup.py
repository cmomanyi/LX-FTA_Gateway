import boto3

# Configuration
REGION = "us-east-1"
SECURITY_GROUP_ID = "sg-0a5dd242e9fa3ef69"  # Replace with your SG ID

ec2 = boto3.client("ec2", region_name=REGION)


def list_enis_using_sg(sg_id):
    print(f"🔍 Checking ENIs using Security Group {sg_id}...\n")
    enis = ec2.describe_network_interfaces(
        Filters=[
            {"Name": "group-id", "Values": [sg_id]}
        ]
    )
    if not enis["NetworkInterfaces"]:
        print("✅ No ENIs found using the security group.")
    else:
        for eni in enis["NetworkInterfaces"]:
            eni_id = eni["NetworkInterfaceId"]
            attached_instance = eni.get("Attachment", {}).get("InstanceId", "Not attached to EC2")
            print(f"❌ ENI in use: {eni_id}, Attached to: {attached_instance}")
        print("\n⚠️ You must detach or delete these ENIs before deleting the SG.\n")


def check_sg_exists(sg_id):
    try:
        response = ec2.describe_security_groups(GroupIds=[sg_id])
        if response["SecurityGroups"]:
            print(f"✅ Security Group found: {response['SecurityGroups'][0]['GroupName']}")
            return True
    except ec2.exceptions.ClientError as e:
        print(f"❌ Error: {e}")
    return False


if __name__ == "__main__":
    if check_sg_exists(SECURITY_GROUP_ID):
        list_enis_using_sg(SECURITY_GROUP_ID)
