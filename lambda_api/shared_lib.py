import json
import os
import urllib


def get_secret(secret_name):
    headers = {"X-Aws-Parameters-Secrets-Token": os.environ.get('AWS_SESSION_TOKEN')}

    secrets_extension_endpoint = "http://localhost:2773" + \
                                 "/secretsmanager/get?secretId=" + \
                                 secret_name

    req = urllib.request.Request(secrets_extension_endpoint, headers=headers)
    response = urllib.request.urlopen(req)
    response_data = response.read().decode('utf-8')

    secret = json.loads(response_data)["SecretString"]
    result = json.loads(secret)
    return result
