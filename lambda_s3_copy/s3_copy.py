import json
import boto3
import urllib
import os

def lambda_handler(event, context):
    BUCKET_NAME = os.environ['s3_bucket']
    url = event['uri'] + "/full/!2048,2048/0/default.jpg"
    filename = event['filename']

    response = urllib.request.urlopen(urllib.request.Request(
        url=url,
        method='GET'),
        timeout=5)
    s3 = boto3.client('s3')
    obj = s3.put_object(Body=response.read(), Bucket=BUCKET_NAME, Key=filename, ContentType=response.headers['Content-Type'])
    response.close()
    return {
        'statusCode': 200,
        'body': {
            'image': event['uri'],
            's3': {
                's3_bucket': BUCKET_NAME,
                's3_key': filename
            }
        }
    }