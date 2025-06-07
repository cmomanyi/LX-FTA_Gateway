import boto3
from botocore.exceptions import ClientError

CLUSTER_NAME = "lx-fta-cluster"
TASK_ID = "32999f8ccd5042ceb2709751e6f62823"
REGION = "us-east-1"
LOG_GROUP = "/ecs/lx-fta-backend"

ecs = boto3.client("ecs", region_name=REGION)
logs = boto3.client("logs", region_name=REGION)
iam = boto3.client("iam", region_name=REGION)


def get_task_details():
    print(f"\n🔍 Fetching task {TASK_ID} in {CLUSTER_NAME}")
    try:
        response = ecs.describe_tasks(cluster=CLUSTER_NAME, tasks=[TASK_ID])
        task = response["tasks"][0]
        return task
    except ClientError as e:
        print("❌ Error fetching task details:", e)
        return None


def get_log_stream_name(task):
    container_id = task["containers"][0]["runtimeId"]
    return f"ecs/fastapi/{container_id}"


def fetch_logs(stream_name):
    print(f"\n📜 Checking CloudWatch logs in stream: {stream_name}")
    try:
        response = logs.get_log_events(logGroupName=LOG_GROUP, logStreamName=stream_name, limit=50)
        for event in response["events"]:
            print(event["message"])
    except ClientError as e:
        print("❌ Failed to fetch logs:", e)


def inspect_task_config(task):
    print("\n⚙️ Task Configuration:")
    print("Task Definition:", task["taskDefinitionArn"])
    print("Network Mode:", task["launchType"])
    print("Subnets and ENIs:", task["attachments"])
    print("Execution Role ARN:", task.get("executionRoleArn", "Not defined"))


def check_iam_policy(role_arn):
    role_name = role_arn.split("/")[-1]
    print(f"\n🔐 Checking IAM policies for role: {role_name}")
    try:
        attached = iam.list_attached_role_policies(RoleName=role_name)
        for policy in attached["AttachedPolicies"]:
            print(f"✅ {policy['PolicyName']}")
    except ClientError as e:
        print("❌ Failed to fetch IAM role policies:", e)


#
# def main():
#     task = get_task_details()
#     if not task:
#         return
#
#     inspect_task_config(task)
#     check_iam_policy(task["executionRoleArn"])
#
#     log_stream = get_log_stream_name(task)
#     fetch_logs(log_stream)
def main():
    task = get_task_details()
    if not task:
        return

    inspect_task_config(task)

    role_arn = task.get("executionRoleArn")
    if role_arn:
        check_iam_policy(role_arn)
    else:
        print(
            "\n⚠️ No executionRoleArn found! This means your task definition may be outdated or missing this setting.")
        print("➡️ Check the ECS task definition and update your service to use the latest revision.\n")

    log_stream = get_log_stream_name(task)
    fetch_logs(log_stream)


if __name__ == "__main__":
    main()
