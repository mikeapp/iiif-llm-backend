import json
import boto3
import urllib

from botocore.exceptions import ClientError


def get_gpt_api_key():
    secret_name = "ai/chatGPT"
    region_name = "us-east-1"
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )
    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        raise e
    response = json.loads(get_secret_value_response['SecretString'])
    return response['key']


def call_gpt(prompt,text):
    response_body = []
    api_url = "https://api.openai.com/v1/chat/completions"
    api_key = get_gpt_api_key()
    if not api_key.endswith('b'):
        raise RuntimeError("Problem with API key: " + api_key[0:5])
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        body = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {
                    "role": "system",
                    "content": "You are an assistant to an archival researcher."
                },
                {
                    "role": "user",
                    "content": text + " " + prompt
                }
            ]
        }
        # Encode the data
        encoded_data = json.dumps(body).encode('utf-8')

        # Make the request
        req = urllib.request.Request(api_url, data=encoded_data, headers=headers)
        response = urllib.request.urlopen(req)

        # Read and decode the response
        response_data = response.read().decode('utf-8')

        # Parse JSON response
        parsed_response = json.loads(response_data)

        # Output the completion
        response_body = parsed_response["choices"][0]["message"]["content"]
    except ClientError as err:
        message = err.response["Error"]["Message"]
        print("A client error occured: " +
              format(message))
    else:
        print("Finished generating text with ChatGPT.")
    return response_body
