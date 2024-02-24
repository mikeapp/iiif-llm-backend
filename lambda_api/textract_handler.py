import json
import boto3
import os
from database import (insert_ocr_record,
                      get_connection)

def lambda_handler(event, context):
    object_id = event['object_id']
    image_id = event['image_id']
    BUCKET_NAME = os.environ['s3_bucket']
    s3_key = event['filename']
    client = boto3.client('textract')
    response = client.detect_document_text(
        Document={
            'S3Object': {
                'Bucket': BUCKET_NAME,
                'Name': s3_key
            }
        }
    )
    Lines=filter(lambda b: b['BlockType'] == 'LINE', response['Blocks'])
    text=""
    for line in Lines:
        text += "  " + line['Text']

    # store text
    conn = get_connection()
    insert_ocr_record(conn, image_id, object_id, 'TEXTRACT', text)
    conn.close()

    # cleanup
    s3client = boto3.client('s3')
    s3client.delete_object(Key=s3_key, Bucket=BUCKET_NAME)
    return {
        'text': json.dumps(text)
    }
