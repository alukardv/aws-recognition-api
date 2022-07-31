import argparse
import time
import boto3
import sys
import os

client = boto3.resource("sns")
NAME_TOPIC = os.environ["SNS_NAME"]

def triggerStream(event, context):
    print(event)
    topic = client.create_topic(Name=NAME_TOPIC)
    try:
        for record in event["Records"]:
            if record['eventName'] == 'INSERT':
                new_record = record['dynamodb']['NewImage']
                print(f"{new_record} was added")
                publish_message(topic, f"NEW:{new_record} was added")
    except Exception as e:
        print(e)
        return "error"


def publish_message(topic, message):
    response = topic.publish(Message=message)
    message_id = response['MessageId']
    return message_id

#     message = "Hello from lambda!"
#     subject = "From  Lambda"
#     send_sns(message, subject)
#
#
# def send_sns(message, subject):
#     TargetArn = 'arn:aws:sns:us-east-1:670726858704:sns-test-m:b9dbb0cb-5a9d-46fc-92af-398d6877d5ca'
#     client.publish(
#         Message=message, Subject=subject, TargetArn=TargetArn)



