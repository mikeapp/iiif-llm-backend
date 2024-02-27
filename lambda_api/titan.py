import json
import logging
import boto3
import math
import urllib

from botocore.exceptions import ClientError

def generate_text(model_id, body):
    print(
        "Generating text with Amazon &titan-text-express; model %s", model_id)

    bedrock = boto3.client(service_name='bedrock-runtime')

    accept = "application/json"
    content_type = "application/json"

    response = bedrock.invoke_model(
        body=body, modelId=model_id, accept=accept, contentType=content_type
    )
    response_body = json.loads(response.get("body").read())

    finish_reason = response_body.get("error")

    if finish_reason is not None:
        raise Exception(f"Text generation error. Error is {finish_reason}")

    print(
        "Successfully generated text with Amazon &titan-text-express; model %s", model_id)

    return response_body


def call_titan(prompt, text):
    response_body = []
    try:
        logging.basicConfig(level=logging.INFO,
                            format="%(levelname)s: %(message)s")

        model_id = 'amazon.titan-text-express-v1'

        body = json.dumps({
            "inputText": text + "\n " + prompt,
            "textGenerationConfig": {
                "maxTokenCount": 4096,
                "stopSequences": [],
                "temperature": 0,
                "topP": 0.1
            }
        })

        response_body = generate_text(model_id, body)

        # parse data from response body
        prompt_tokens = response_body['inputTextTokenCount']
        completion_tokens = response_body['results'][0]['tokenCount']
        response_text = response_body['results'][0]['outputText']
        cost = math.ceil((prompt_tokens + completion_tokens) / 1000)

        result = {
            "text": response_text,
            "usage": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "credits": cost
            },
            "response": response_body
        }

    except ClientError as err:
        message = err.response["Error"]["Message"]
        return {"error": format(message)}

    else:
        print(f"Finished generating text with the Amazon &titan-text-express; model {model_id}.")

    return result
