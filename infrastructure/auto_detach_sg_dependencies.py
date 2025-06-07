import boto3
import time

REGION = "us-east-1"
SG_ID = "sg-0a5dd242e9fa3ef69"

ec2 = boto3.client("ec2", region_name=REGION)
ecs = boto3.client("ecs", region_name=REGION)


def find_ec2_dependencies(sg_id):
    print(f"🔍 Checking EC2 network interfaces using SG {sg_id}...")
    enis = ec2.describe_network_interfaces(
        Filters=[{"Name": "group-id", "Values": [sg_id]}]
    ).get("NetworkInterfaces", [])

    for eni in enis:
        eni_id = eni["NetworkInterfaceId"]
        print(f"❌ ENI {eni_id} using SG. Trying to detach or delete...")

        if eni.get("Attachment"):
            try:
                ec2.detach_network_interface(AttachmentId=eni["Attachment"]["AttachmentId"], Force=True)
                print(f"✅ Detached ENI: {eni_id}")
                time.sleep(2)
            except Exception as e:
                print(f"⚠️ Failed to detach ENI: {e}")

        try:
            ec2.delete_network_interface(NetworkInterfaceId=eni_id)
            print(f"✅ Deleted ENI: {eni_id}")
        except Exception as e:
            print(f"⚠️ Failed to delete ENI: {e}")


def stop_ecs_services_using_sg(sg_id):
    print(f"🔍 Searching ECS services in all clusters using SG {sg_id}...")
    clusters = ecs.list_clusters()["clusterArns"]

    for cluster_arn in clusters:
        services = ecs.list_services(cluster=cluster_arn)["serviceArns"]
        for service_arn in services:
            service = ecs.describe_services(cluster=cluster_arn, services=[service_arn])["services"][0]

            if service["launchType"] != "FARGATE":
                continue

            task_def = ecs.describe_task_definition(taskDefinition=service["taskDefinition"])
            eni_sgs = task_def["taskDefinition"]["networkMode"] == "awsvpc"

            if eni_sgs:
                print(f"❌ ECS Service using SG found: {service_arn}")
                print("🛑 Stopping service...")
                try:
                    ecs.update_service(cluster=cluster_arn, service=service_arn, desiredCount=0)
                    print("✅ Service stopped.")
                except Exception as e:
                    print(f"⚠️ Failed to stop service: {e}")


def delete_sg(sg_id):
    print(f"\n🧹 Attempting to delete security group {sg_id}...")
    try:
        ec2.delete_security_group(GroupId=sg_id)
        print("✅ Security group deleted.")
    except Exception as e:
        print(f"❌ Could not delete SG: {e}")


if __name__ == "__main__":
    find_ec2_dependencies(SG_ID)
    stop_ecs_services_using_sg(SG_ID)
    delete_sg(SG_ID)
