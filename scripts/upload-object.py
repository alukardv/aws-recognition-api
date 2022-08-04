import json
import os
import requests
import boto3
import uuid
from botocore.config import Config


BUCKET_NAME = os.environ['BUCKET']


def createBlob(event, context):
    print(event)
    global callback_url
    try:
        callback_url = json.loads(event['body']).get('callback_url')

        if not callback_url:
            return {"statusCode": 404, "body": json.dumps({"error": "URL not found"})}

        s3 = boto3.client("s3", config=Config(signature_version='s3v4'))
        blob_id = str(uuid.uuid1())

        upload_url = s3.generate_presigned_url("put_object", Params={"Bucket": BUCKET_NAME, "Key": blob_id}, ExpiresIn=3600)
    except Exception as e:
        print(e)
    else:
        return {
            "statusCode": 201,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"blob_id": blob_id, 'callback_url': callback_url, "upload_url": upload_url}),
        }

    try:
        new_record = ''
        result = ''
        for record in event["Records"]:
            if record['eventName'] == 'INSERT':
                new_record = record['dynamodb']['NewImage']
                imageLabels = []
                for label in new_record['labels'].get('L'):
                    imageParents = []
                    for labelP in label.get('M').get('parents').get('L'):
                        imageParents.append(labelP.get('S'))
                    imageLabels.append({'label': label.get('M').get('label').get('S'),
                                        'confidence': label.get('M').get('confidence').get('S'),
                                        'parents': imageParents})

                result = {'blob_id': new_record.get('blob_id').get('S'),
                          'labels': imageLabels
                          }
                print(f"{new_record} was added")
                print(f"result {result}")
    except Exception as e:
        print(e)
    else:
        url = callback_url

        payload = json.dumps(result)
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        print(response)
