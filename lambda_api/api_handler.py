from database import hello_world
import boto3

def lambda_handler(event, context):
    message = hello_world()
    return {
        'message': message
    }