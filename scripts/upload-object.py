import json
import os
import boto3
import uuid
from botocore.config import Config


def createBlob(event, context):

    DNS_RECORD = os.environ["DNS_RECORD"]
    BUCKET_NAME = os.environ['BUCKET']

    s3 = boto3.client("s3", config=Config(signature_version='s3v4'))
    file_name = str(uuid.uuid1())

    #post request
    # URL = s3.generate_presigned_post(
    #     Bucket=BUCKET_NAME, Key=file_name, Fields=None, Conditions=None, ExpiresIn=3600
    # )

    URL = s3.generate_presigned_url("put_object", Params={"Bucket": BUCKET_NAME, "Key": file_name}, ExpiresIn=3600)

    callback_url = DNS_RECORD + '/blobs/' + file_name

    if not URL:
        return {"statusCode": 404, "body": json.dumps({"error": "URL not found"})}

    return {
        "statusCode": 201,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"URL": URL, "blobs_id": file_name, 'callback_url': callback_url}),
    }
