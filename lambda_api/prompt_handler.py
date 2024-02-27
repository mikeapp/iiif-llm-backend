import json
from database import (get_generic_prompts, get_connection, auth_user)

def lambda_handler(event, context):
    cognito = event['cognito']
    auth_user(cognito)
    conn = get_connection()
    prompts = get_generic_prompts(conn)
    conn.close()
    result = {
        "prompts": prompts
    }
    return result


