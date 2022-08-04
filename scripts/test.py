import boto3
import json

def test(event, context):
    print(event)
    return {"statusCode": 200, "body": 'ok'}