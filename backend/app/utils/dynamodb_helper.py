import boto3

dynamodb = boto3.resource("dynamodb")


def put_item(table_name: str, item: dict):
    table = dynamodb.Table(table_name)
    table.put_item(Item=item)
