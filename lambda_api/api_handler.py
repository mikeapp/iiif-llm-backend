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


def lambda_handler(event, context):
    body = event['body']
    object_id = body['object_id']
    image_ids = body['image_ids']
    prompt_id = body['prompt_id']
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

    gpt_completion = ""  # call_gpt("Please translate this Latin text", "nautae dant dona feminis")
    titan_completion = "" # call_titan("what is the answer?", " 2 * 2")

    insert_activity_record(conn, user['username'], object_id, "ChatGPT", 2)

    response = {
        'user': user,
        'credits_used': credits_used_to_date,
        'gpt': gpt_completion,
        'titan': titan_completion
    }

    return response
