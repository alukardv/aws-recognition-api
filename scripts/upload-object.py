import json
import os
import http.client
import boto3
import uuid
from botocore.config import Config
from botocore.exceptions import ClientError

NAME_TOPIC = os.environ["SNS_NAME"]
DNS_RECORD = os.environ["DNS_RECORD"]
BUCKET_NAME = os.environ['BUCKET']
client_res = boto3.resource("sns")
sns_client = boto3.client('sns')
TABLE_NAME = os.environ["TABLE_NAME"]
dynamodb_client = boto3.client("dynamodb")


def callback_url(event, context):
    print(event)
    try:
        blobs_id = event["pathParameters"]["blobs_id"]
        db_record = dynamodb_client.get_item(
            TableName=TABLE_NAME,
            Key={"blobs_id": {"S": blobs_id}}).get('Item')

        imageLabels = []
        for label in db_record['labels'].get('L'):
            imageParents = []
            for labelP in label.get('M').get('parents').get('L'):
                imageParents.append(labelP.get('S'))
            imageLabels.append({'label': label.get('M').get('label').get('S'),
                                'confidence': label.get('M').get('confidence').get('S'),
                                'parents': imageParents})

        result = {'blobs_id': db_record.get('blobs_id').get('S'),
                  'labels': imageLabels
                  }

    except Exception as e:
        result = None
        print(e)

    if not result:
        return {"statusCode": 404, "body": json.dumps({"error": "URL not found"})}

    return {"statusCode": 200, "body": json.dumps(result)}


def createBlob(event, context):
    print(event)

    callback_url = json.loads(event['body']).get('callback_url')

    callback_blobs_id = callback_url[len(DNS_RECORD)+1:]
    db_record = dynamodb_client.get_item(
        TableName=TABLE_NAME,
        Key={"blobs_id": {"S": callback_blobs_id}}).get('Item')
    print(db_record)

    if not db_record:
        return {"statusCode": 404, "body": json.dumps({"error": "URL not found"})}

    s3 = boto3.client("s3", config=Config(signature_version='s3v4'))
    blobs_id = str(uuid.uuid1())

    URL = s3.generate_presigned_url("put_object", Params={"Bucket": BUCKET_NAME, "Key": blobs_id}, ExpiresIn=3600)

    return {
        "statusCode": 201,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"URL": URL, "blobs_id": blobs_id, 'callback_url': callback_url}),
    }


def subscribe(topic, protocol, endpoint):
    try:
        subscription = sns_client.subscribe(
            TopicArn=topic,
            Protocol=protocol,
            Endpoint=endpoint,
            ReturnSubscriptionArn=True)
    except ClientError as e:
        print(e)
        raise
    else:
        return subscription


def confirm_subscribe(topic, token):
    try:
        confirm1 = sns_client.confirm_subscription(
            TopicArn=topic,
            Token=token,
        )
    except ClientError as e:
        print(e)
        raise
    else:
        return confirm1


# def list_topic_subscriptions(topic_arn):
#     try:
#         paginator = sns_client.get_paginator('list_subscriptions_by_topic')
#         page_iterator = paginator.paginate(TopicArn=topic_arn,
#                                            PaginationConfig={'MaxItems': 100})
#         topic_subscriptions = []
#         for page in page_iterator:
#             for subscription in page['Subscriptions']:
#                 topic_subscriptions.append(subscription)
#     except ClientError as e:
#         print(e)
#         raise
#     else:
#         return topic_subscriptions
