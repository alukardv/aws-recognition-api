import json
import boto3
import os
import http.client

dynamodb_client = boto3.client("dynamodb")
TABLE_NAME = os.environ["TABLE_NAME"]
client_sns = boto3.resource("sns")
NAME_TOPIC = os.environ["SNS_NAME"]
DNS_RECORD = os.environ["DNS_RECORD"]


def getImagesByLabel(event, context):
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

    # topic = client_sns.create_topic(Name=NAME_TOPIC)
    try:
        for record in event["Records"]:
            if record['eventName'] == 'INSERT':
                # print(record['dynamodb']['NewImage'])
                new_record = record['dynamodb']['NewImage']['blobs_id']
                print(f"{new_record} was added")

                #publish_message(topic, str(result_sns))
    except Exception as e:
        print(e)
        #return "error"

    if not result:
        return {"statusCode": 404, "body": json.dumps({"error": "Blob not found"})}

    response = {"statusCode": 200, "body": json.dumps(result)}
    return response


# def publish_message(topic, message):
#     response = topic.publish(Message=message)
#     message_id = response['MessageId']
#     return message_id