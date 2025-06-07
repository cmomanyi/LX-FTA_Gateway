import boto3
from botocore.exceptions import ClientError

region = "us-east-1"
sg_id = "sg-0a5dd242e9fa3ef69"

ec2 = boto3.client("ec2", region_name=region)
ecs = boto3.client("ecs", region_name=region)

def detach_and_delete_enis():
    try:
        enis = ec2.describe_network_interfaces(
            Filters=[{"Name": "group-id", "Values": [sg_id]}]
        )["NetworkInterfaces"]

        for eni in enis:
            eni_id = eni["NetworkInterfaceId"]
            print(f"❌ ENI {eni_id} is using SG.")

            attachment = eni.get("Attachment")
            if attachment:
                attach_id = attachment["AttachmentId"]
                try:
                    print(f"🔌 Attempting detach: {eni_id}")
                    ec2.detach_network_interface(AttachmentId=attach_id, Force=True)
                except ClientError as e:
                    print(f"⚠️ Detach failed: {e}")

            try:
                print(f"🧹 Trying to delete: {eni_id}")
                ec2.delete_network_interface(NetworkInterfaceId=eni_id)
            except ClientError as e:
                print(f"⚠️ Delete failed: {e}")
    except ClientError as e:
        print(f"💥 ENI fetch failed: {e}")

def stop_ecs_services():
    try:
        clusters = ecs.list_clusters()["clusterArns"]
        for cluster in clusters:
            services = ecs.list_services(cluster=cluster)["serviceArns"]
            for service_arn in services:
                service_desc = ecs.describe_services(cluster=cluster, services=[service_arn])["services"][0]
                if sg_id in service_desc.get("networkConfiguration", {}).get("awsvpcConfiguration", {}).get("securityGroups", []):
                    print(f"🛑 Stopping ECS service: {service_arn}")
                    ecs.update_service(cluster=cluster, service=service_arn, desiredCount=0)
    except ClientError as e:
        print(f"💥 ECS Service error: {e}")

if __name__ == "__main__":
    stop_ecs_services()
    detach_and_delete_enis()
