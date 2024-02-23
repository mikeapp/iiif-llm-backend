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
    conn = get_connection()
    # message = create_user_record(conn,"mikea", "michael.appleby@yale.edu", 500)
    insert_activity_record(conn, 'mikea', 'https://foo/bar/123', "ChatGPT", 2)
    user = get_user_by_username(conn, 'mikea')
    credits_used = get_credits_used_by_username(conn, 'mikea')

    gpt_completion = ""  # call_gpt("Please translate this Latin text", "nautae dant dona feminis")
    titan_completion = "" # call_titan("what is the answer?", " 2 * 2")
    return {
        'user': user,
        'credits_used': credits_used,
        'gpt': gpt_completion,
        'titan': titan_completion
    }