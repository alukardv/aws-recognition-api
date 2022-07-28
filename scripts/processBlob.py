import json
import boto3
import os
import uuid


def labelOnS3Upload(event, context):
    bucket = os.environ['BUCKET']

    filesUploaded = event['Records']

    for file in filesUploaded:
        fileName = file["s3"]["object"]["key"]
        rekognitionClient = boto3.client('rekognition')
        response = rekognitionClient.detect_labels(Image={'S3Object': {'Bucket': bucket, 'Name': fileName}}, MaxLabels=5)

        imageLabels = []
        for label in response['Labels']:
            imageLabels.append(label["Name"].lower())

    dynamodb = boto3.resource('dynamodb')
    addLabelTablefnc(dynamodb=dynamodb, fileName=fileName, labels=imageLabels)


def addLabelTablefnc(dynamodb, fileName, labels):
    Table = dynamodb.Table(os.environ['TABLE_NAME'])
    item = {'fileName': fileName, 'labels': labels}

    Table.put_item(Item=item)

    response = {
        "statusCode": 200,
        "body": json.dumps(item)
    }
    return response
