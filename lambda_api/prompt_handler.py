import json
from database import (get_generic_prompts, get_connection, find_or_create_user)

def lambda_handler(event, context):
    conn = get_connection()
    prompts = get_generic_prompts(conn)
    result = {
        "prompts": prompts
    }
    return result


