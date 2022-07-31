import json
import boto3
import os


def labelOnS3Upload(event, context):
    bucket = os.environ['BUCKET']

    filesUploaded = event['Records']

    for file in filesUploaded:
        blobs_id = file["s3"]["object"]["key"]
        rekognitionClient = boto3.client('rekognition')
        response = rekognitionClient.detect_labels(Image={'S3Object': {'Bucket': bucket, 'Name': blobs_id}}, MaxLabels=5)

        confidence = str(response['Labels'][0].get('Confidence'))

        imageLabels = []
        for label in response['Labels'][0].get('Parents'):
            imageLabels.append(label['Name'].lower())

    dynamodb = boto3.resource('dynamodb')
    addLabelTablefnc(dynamodb=dynamodb, blobs_id=blobs_id, confidence=confidence, labels=imageLabels)


def addLabelTablefnc(dynamodb, blobs_id, confidence, labels):
    Table = dynamodb.Table(os.environ['TABLE_NAME'])
    item = {'blobs_id': blobs_id, 'labels': [{'label': 'string', 'confidence': confidence, 'parents': labels}]}

    Table.put_item(Item=item)

    response = {
        "statusCode": 200,
        "body": json.dumps(item)
    }
    return response
