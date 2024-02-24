from database import (create_user_record,
                      get_user_by_username,
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
    manifest_image_ids = list(map(lambda c: c['image_id'], manifest_info['canvases']))
    print(manifest_image_ids)
    requested_ids = set(image_ids)
    valid_image_ids = list(filter(lambda c: c in requested_ids, manifest_image_ids))
    print(valid_image_ids)
    unprocessed_image_ids = list(filter(lambda image_id: not get_ocr(conn, image_id, object_id), valid_image_ids))
    return unprocessed_image_ids

def start_state_machine(input):
    session = boto3.Session()
    step_client = session.client('stepfunctions')

    response = step_client.start_execution(
        input= json.dumps(input),
        stateMachineArn=os.environ['state_machine']
    )
    return response['executionArn']


def lambda_handler(event, context):
    object_id = event['object_id']
    image_ids = filter_array_uris(event['image_ids'])

    conn = get_connection()
    user = find_or_create_user(event, conn)

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

    return {
        'user': user,
        'credits_used': cost,
        'object_id': object_id,
        'new_image_ids': new_image_ids,
        'job_id': job_id
    }