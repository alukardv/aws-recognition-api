import json
import boto3
import os

dynamodb_client = boto3.client("dynamodb")
TABLE_NAME = os.environ["TABLE_NAME"]


def getImagesByLabel(event, context):
    print(event)
    try:
        blob_id = event["pathParameters"]["blob_id"]
        db_record = dynamodb_client.get_item(
            TableName=TABLE_NAME,
            Key={"blob_id": {"S": blob_id}}).get('Item')

        imageLabels = []
        for label in db_record['labels'].get('L'):
            imageParents = []
            for labelP in label.get('M').get('parents').get('L'):
                imageParents.append(labelP.get('S'))
            imageLabels.append({'label': label.get('M').get('label').get('S'),
                                'confidence': label.get('M').get('confidence').get('S'),
                                'parents': imageParents})

        result = {'blob_id': db_record.get('blob_id').get('S'),
                  'labels': imageLabels
                  }

    except Exception as e:
        result = None
        print(e)

    if not result:
        return {"statusCode": 404, "body": json.dumps({"error": "Blob not found"})}

    response = {"statusCode": 200, "body": json.dumps(result)}
    return response
