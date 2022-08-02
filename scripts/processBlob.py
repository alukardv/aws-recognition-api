import json
import boto3
import os

client_sns = boto3.resource("sns")
NAME_TOPIC = os.environ["SNS_NAME"]


def labelOnS3Upload(event, context):
    bucket = os.environ['BUCKET']
    filesUploaded = event['Records']

    for file in filesUploaded:
        blobs_id = file["s3"]["object"]["key"]
        rekognitionClient = boto3.client('rekognition')
        response = rekognitionClient.detect_labels(Image={'S3Object': {'Bucket': bucket, 'Name': blobs_id}}, MaxLabels=5)

        print(response)

        imageLabels = []
        for label in response['Labels']:
            imageParents = []
            for labelP in label['Parents']:
                imageParents.append(labelP['Name'])
            imageLabels.append({'label': label['Name'],
                                'confidence': str(label['Confidence']),
                                'parents': imageParents})

        print(imageLabels)

    dynamodb = boto3.resource('dynamodb')
    addLabelTablefnc(dynamodb=dynamodb, blobs_id=blobs_id, labels=imageLabels)

    # topic = client_sns.create_topic(Name=NAME_TOPIC)
    # if not addLabelTablefnc:
    #     publish_message(topic, str(message))


def addLabelTablefnc(dynamodb, blobs_id, labels):
    Table = dynamodb.Table(os.environ['TABLE_NAME'])
    item = {'blobs_id': blobs_id, 'labels': labels}

    Table.put_item(Item=item)

    response = {
        "statusCode": 200,
        "body": json.dumps(item)
    }
    return response


# def publish_message(topic, message):
#     response = topic.publish(Message=message)
#     message_id = response['MessageId']
#     return message_id
