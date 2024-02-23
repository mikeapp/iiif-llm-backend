from database import (create_user_record,
                      get_user_by_username,
                      get_connection,
                      insert_activity_record,
                      get_credits_used_by_username,
                      get_ocr,
                      get_generic_prompt_by_key)
from chatgpt import call_gpt
from titan import call_titan
import boto3


def lambda_handler(event, context):
    # object_id = event['object_id']
    # image_ids = event['image_ids']
    # prompt_id = event['prompt_id']
    username = event['username']
    email = event['email']

    conn = get_connection()

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
    if credits_used > user['credits']:
        return {"error": "Credit limit exceeded"}

    gpt_completion = ""  # call_gpt("Please translate this Latin text", "nautae dant dona feminis")
    titan_completion = "" # call_titan("what is the answer?", " 2 * 2")

    insert_activity_record(conn, username, object_id, "ChatGPT", 2)

    return {
        'user': user,
        'credits_used': credits_used,
        'gpt': gpt_completion,
        'titan': titan_completion
    }