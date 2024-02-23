import json
import os
import urllib


def filter_array_uris(arr):
    if type(arr) != list:
        return []
    return filter(lambda s: s.startswith('https://'), arr)

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


def map_manifest(uri):
    response = urllib.request.urlopen(
        urllib.request.Request(url=uri, method='GET'),
        timeout=5
    )
    canvases = []
    manifest = ""
    statusCode = 500
    responseBody = {}
    if response.headers['Content-Type'].startswith('application/json'):
        body = response.read().decode("utf-8")
        manifest = json.loads(body)
        # .items.*.items.*.items[0].body.service[0]['@id']
        for canvas in manifest['items']:
            for anno_page in canvas['items']:
                anno = anno_page['items'][0]
                service = anno['body']['service'][0]
                image = service['@id']
                canvases.append({
                    'imageId': image,
                    'id': canvas['id']
                })
        statusCode = 200
    return {
        "statusCode": statusCode,
        "uri": uri,
        "canvases": canvases
    }