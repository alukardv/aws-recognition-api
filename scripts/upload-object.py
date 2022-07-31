import json
import os
import boto3
import uuid
from botocore.config import Config
from botocore.exceptions import ClientError

NAME_TOPIC = os.environ["SNS_NAME"]
DNS_RECORD = os.environ["DNS_RECORD"]
BUCKET_NAME = os.environ['BUCKET']
client_res = boto3.resource("sns")
sns_client = boto3.client('sns')


def callback_url(event, context):
    print(event)
    topic = str(client_res.create_topic(Name=NAME_TOPIC))[15:][:-2]
    if event['body'] is not None:
        body_Token = json.loads(event['body']).get('Token')
        confirm_subscribe(topic, body_Token)


def createBlob(event, context):
    print(event)
    s3 = boto3.client("s3", config=Config(signature_version='s3v4'))
    blobs_id = str(uuid.uuid1())
    topic = str(client_res.create_topic(Name=NAME_TOPIC))[15:][:-2]

    callback_url = DNS_RECORD + '/' + blobs_id

    subscribe(topic, 'https', callback_url)

    # post request
    # URL = s3.generate_presigned_post(
    #     Bucket=BUCKET_NAME, Key=file_name, Fields=None, Conditions=None, ExpiresIn=3600
    # )

    URL = s3.generate_presigned_url("put_object", Params={"Bucket": BUCKET_NAME, "Key": blobs_id}, ExpiresIn=3600)

    if not URL:
        return {"statusCode": 404, "body": json.dumps({"error": "URL not found"})}

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
