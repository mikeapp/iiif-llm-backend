from database import hello_world


def lambda_handler(event, context):
    message = hello_world()
    return {
        'message': message
    }