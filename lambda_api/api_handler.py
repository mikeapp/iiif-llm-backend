from database import hello_world
from chatgpt import call_gpt
import boto3

def lambda_handler(event, context):
    message = hello_world()
    completion = call_gpt("Please translate this Latin text", "nautae dant dona feminis")
    return {
        'message': message,
        'completion': completion
    }