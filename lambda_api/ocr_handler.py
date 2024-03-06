from database import (auth_user,
                      get_connection,
                      insert_activity_record,
                      get_credits_used_by_username,
                      get_ocr,
                      get_generic_prompt_by_key,
                      find_or_create_user)
from shared_lib import (filter_array_uris, map_manifest)
import boto3
import json
import os


def get_unprocessed_uris(conn, object_id, image_ids):
    if not object_id.startswith('https://collections.library.yale.edu/manifests/'):
        raise RuntimeError('Manifest URI is not from Yale Digital Collections')
    manifest_info = map_manifest(object_id)
    manifest_image_ids = set(map(lambda c: c['image_id'], manifest_info['canvases']))
    requested_ids = set(image_ids)
    valid_image_ids = requested_ids.intersection(manifest_image_ids)
    ocr_entries = get_ocr(conn, object_id)
    ocr_ids = set([])
    if ocr_entries is not None:
        ocr_ids = set(map(lambda e: e['image_id'], ocr_entries))
    return list(valid_image_ids.difference(ocr_ids))


def start_state_machine(input):
    session = boto3.Session()
    step_client = session.client('stepfunctions')

    response = step_client.start_execution(
        input= json.dumps(input),
        stateMachineArn=os.environ['state_machine']
    )
    return response['executionArn']

def check_state_machine(arn):
    session = boto3.Session()
    step_client = session.client('stepfunctions')
    response = step_client.describe_execution(executionArn=arn)
    return response['status']

def lambda_handler(event, context):
    body = event['body']
    # if status check
    if 'job_id' in body:
        return {
            "status": check_state_machine(body['job_id'])
        }

    object_id = body['object_id']
    image_ids = filter_array_uris(body['image_ids'])
    cognito = event['cognito']
    auth_user(cognito)
    conn = get_connection()
    user = find_or_create_user(cognito, conn)

    cost = None
    job_id = None
    new_image_ids = get_unprocessed_uris(conn, object_id, image_ids)

    if len(new_image_ids) > 0:
        cost = len(new_image_ids)
        # check credit balance
        credits_used_user = get_credits_used_by_username(conn, user['username'])
        credits_used = 0
        if credits_used_user:
            credits_used = credits_used_user['credits_used']
        if credits_used + cost > user['credits']:
            return {"error": "Operation would exceed credit limit"}

        insert_activity_record(conn, user['username'], object_id, "TEXTRACT", cost)
        job_input = {
            'object_id': object_id,
            'image_ids': new_image_ids
        }
        job_id = start_state_machine(job_input)

    conn.close()
    response = {
        'user': user,
        'credits_used': cost,
        'object_id': object_id,
        'new_image_ids': new_image_ids,
        'job_id': job_id
    }

    return response