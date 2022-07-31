import json
import boto3
import os

dynamodb_client = boto3.client("dynamodb")
client_sns = boto3.resource("sns")
TABLE_NAME = os.environ["TABLE_NAME"]
NAME_TOPIC = os.environ["SNS_NAME"]
DNS_RECORD = os.environ["DNS_RECORD"]


def getImagesByLabel(event, context):
    #print(event)
    try:
        blobs_id = event["pathParameters"]["blobs_id"]
        db_record = dynamodb_client.get_item(
            TableName=TABLE_NAME,
            Key={"blobs_id": {"S": blobs_id}}).get('Item')

        parents = []
        for parents_label in db_record.get('labels').get('L')[0].get('M').get('parents').get('L'):
            parents.append(parents_label['S'])


        result = {'blobs_id': db_record.get('blobs_id').get('S'),
                  'labels': [{'label': db_record.get('labels').get('L')[0].get('M').get('label').get('S'),
                              'confidence': db_record.get('labels').get('L')[0].get('M').get('confidence').get('S'),
                              'parents': parents
                              }]}

    except Exception as e:
        result = None
        print(e)

    topic = client_sns.create_topic(Name=NAME_TOPIC)
    try:
        for record in event["Records"]:
            if record['eventName'] == 'INSERT':
                print(record['dynamodb']['NewImage'])
                new_record = record['dynamodb']['NewImage']
                parents_sns = []
                for parents_label in new_record.get('labels').get('L')[0].get('M').get('parents').get('L'):
                    parents_sns.append(parents_label['S'])

                result_sns = {'blobs_id': new_record.get('blobs_id').get('S'),
                          'labels': [{'label': new_record.get('labels').get('L')[0].get('M').get('label').get('S'),
                                      'confidence': new_record.get('labels').get('L')[0].get('M').get('confidence').get(
                                          'S'),
                                      'parents': parents_sns
                                      }]}

                print(f"{result_sns} was added")

                publish_message(topic, str(result_sns))
    except Exception as e:
        print(e)
        #return "error"

    if not result:
        return {"statusCode": 404, "body": json.dumps({"error": "Blob not found"})}

    response = {"statusCode": 200, "body": json.dumps(result)}
    return response


def publish_message(topic, message):
    response = topic.publish(Message=message)
    message_id = response['MessageId']
    return message_id