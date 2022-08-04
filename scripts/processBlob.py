import json
import boto3
import os


def labelOnS3Upload(event, context):
    bucket = os.environ['BUCKET']
    filesUploaded = event['Records']

    for file in filesUploaded:
        blob_id = file["s3"]["object"]["key"]
        rekognitionClient = boto3.client('rekognition')
        response = rekognitionClient.detect_labels(Image={'S3Object': {'Bucket': bucket, 'Name': blob_id}}, MaxLabels=5)

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
    addLabelTablefnc(dynamodb=dynamodb, blob_id=blob_id, labels=imageLabels)


def addLabelTablefnc(dynamodb, blob_id, labels):
    Table = dynamodb.Table(os.environ['TABLE_NAME'])
    item = {'blob_id': blob_id, 'labels': labels}

    Table.put_item(Item=item)

    response = {
        "statusCode": 200,
        "body": json.dumps(item)
    }
    return response
