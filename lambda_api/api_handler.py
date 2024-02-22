from database import hello_world
from chatgpt import call_gpt
from titan import call_titan
import boto3

def lambda_handler(event, context):
    message = hello_world()
    gpt_completion = call_gpt("Please translate this Latin text", "nautae dant dona feminis")
    titan_completion = call_titan("what is the answer?", " 2 * 2")
    return {
        'message': message,
        'gpt': gpt_completion,
        'titan': titan_completion
    }