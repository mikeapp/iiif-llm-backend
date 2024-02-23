from database import (create_user_record,
                      get_user_by_username,
                      get_connection,
                      insert_activity_record,
                      get_credits_used_by_username,
                      get_ocr,
                      get_generic_prompt_by_key)
from shared_lib import (filter_array_uris, map_manifest)
import boto3


def get_unprocessed_uris(conn, object_id, image_ids):
    if not object_id.startswith('https://collections.library.yale.edu/manifests/'):
        raise RuntimeError('Manifest URI is not from Yale Digital Collections')
    manifest_info = map_manifest(object_id)
    requested_ids = set(image_ids)
    valid_image_ids = list(filter(lambda c: c in requested_ids, manifest_info['canvases']))
    unprocessed_image_ids = list(filter(lambda image_id: get_ocr(conn, object_id, image_id), valid_image_ids))
    return unprocessed_image_ids

def lambda_handler(event, context):
    object_id = event['object_id']
    image_ids = filter_array_uris(event['image_ids'])
    # prompt_id = event['prompt_id']
    username = event['username']
    email = event['email']
    conn = get_connection()
    new_image_ids = get_unprocessed_uris(conn, object_id, image_ids)
    cost = len(new_image_ids)

    # load or create user
    user = get_user_by_username(conn, username)
    if user is None:
        create_user_record(conn, username, email, 500)
        user = get_user_by_username(conn, username)

    # check credit balance
    credits_used_user = get_credits_used_by_username(conn, username)
    credits_used = 0
    if credits_used_user:
        credits_used = credits_used_user['credits_used']
    if credits_used + cost > user['credits']:
        return {"error": "Operation would exceed credit limit"}

    insert_activity_record(conn, username, object_id, "TEXTRACT", cost)

    return {
        'user': user,
        'credits_used': cost,
        'new_image_ids': new_image_ids
    }