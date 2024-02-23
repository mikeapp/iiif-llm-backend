from database import create_user_record, get_user_by_username
from chatgpt import call_gpt
from titan import call_titan
import boto3

def lambda_handler(event, context):
    message = create_user_record("mikea", "michael.appleby@yale.edu", 500)
    user = get_user_by_username('mikea')
    gpt_completion = ""  # call_gpt("Please translate this Latin text", "nautae dant dona feminis")
    titan_completion = "" # call_titan("what is the answer?", " 2 * 2")
    return {
        'user': user,
        'message': message,
        'gpt': gpt_completion,
        'titan': titan_completion
    }