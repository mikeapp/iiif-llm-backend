# Backend for IIIF LLM Workbench

## API Structure

Resources:

- /ai-api-v1
  - /ocr POST
  - /model POST
  - /prompt GET

## Authorization

Include an ID token in the authorization header"
`Authorization: TOKEN_VALUE_XXXXXX`

Obtain a token from a valid client using the AWS CLI:
`aws cognito-idp initiate-auth --auth-flow USER_PASSWORD_AUTH --client-id $CLIENT_ID --auth-parameters USERNAME=$USERNAME,PASSWORD=$PASSWORD`
