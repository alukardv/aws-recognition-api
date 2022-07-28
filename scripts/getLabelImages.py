import json
import boto3
import os


def getImagesByLabel(event, context):
    dynamodb_client = boto3.client("dynamodb")
    bucket = os.environ['BUCKET']
    TABLE_NAME = os.environ["TABLE_NAME"]

    blobs_id = event["pathParameters"]["blobs_id"]
    print(blobs_id)

    result = dynamodb_client.get_item(
        TableName=TABLE_NAME,
        Key={"fileName": {"S": blobs_id}}).get("Item")
    print({"fileName": {"S": blobs_id}})
    print(result)

    if not result:
        return {"statusCode": 404, "body": json.dumps({"error": "Blob not found"})}

    labels = result.get("labels").get("L")

    response = {"statusCode": 200, "body": json.dumps(labels)}
    return response
