from database import (create_user_record,
                      get_user_by_username,
                      get_connection,
                      insert_activity_record,
                      get_credits_used_by_username,
                      get_ocr,
                      get_generic_prompt_by_key,
                      auth_user,
                      find_or_create_user)
from chatgpt import call_gpt
from titan import call_titan
import boto3
import json


def assemble_document(conn, image_ids, object_id):
    ocr = get_ocr(conn, image_ids, object_id)
    if ocr is None:
        raise Exception("No OCR")
    pages = {}
    for image in ocr:
        pages[image['image_id']] = image
    doc = ""
    for image_id in image_ids:
        page = pages[image_id]
        doc = doc + page['text_content'] + " "
    return doc

def lambda_handler(event, context):
    body = event['body']
    object_id = body['object_id']
    image_ids = body['image_ids']
    prompt_id = body['prompt_id']
    model = body['model']
    cognito = event['cognito']

    auth_user(cognito)
    conn = get_connection()
    user = find_or_create_user(cognito, conn)

    # check credit balance
    credits_used_to_date = get_credits_used_by_username(conn, user['username'])
    credits_used = 0
    if credits_used_to_date:
        credits_used = credits_used_to_date['credits_used']
    if credits_used > user['credits']:
        return {"error": "Credit limit exceeded"}

    # load prompt
    prompt = get_generic_prompt_by_key(conn, prompt_id)

    # load text
    doc = assemble_document(conn, image_ids, object_id)
    doc = "<doc>" + doc + "</doc>"

    if model == 'chatgpt-3.5' or model == 'chatgpt-4':
        completion = call_gpt(prompt['prompt_text'], doc, model)
    elif model == 'titan-1':
        completion = call_titan(prompt['prompt_text'], doc)
    else:
        raise Exception('Invalid model')

    credits_used_this_call = completion['usage']['credits']
    credits_remaining = user['credits'] - credits_used - credits_used_this_call
    user['credits'] = credits_remaining
    insert_activity_record(conn, user['username'], object_id, model, credits_used_this_call)
    conn.close()

    response = {
        'user': user,
        'completion': completion
    }

    return response
