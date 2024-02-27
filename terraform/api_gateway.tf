resource "aws_api_gateway_rest_api" "api" {
  name        = "ai-api"
  description = "IIIF LLM API Gateway"
  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

# Authorizer
resource "aws_api_gateway_authorizer" "cognito_authorizer" {
  name = "CognitoAuthorizer"
  type = "COGNITO_USER_POOLS"
  rest_api_id = aws_api_gateway_rest_api.api.id
  provider_arns = [ var.cognito_arn ]
}

# Resources
resource "aws_api_gateway_resource" "api" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  path_part   = "ai-api-v1"
}

resource "aws_api_gateway_resource" "model" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_resource.api.id
  path_part   = "model"
}

resource "aws_api_gateway_resource" "ocr" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_resource.api.id
  path_part   = "ocr"
}

resource "aws_api_gateway_resource" "prompt" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_resource.api.id
  path_part   = "prompt"
}

# /model
resource "aws_api_gateway_method" "model" {
  rest_api_id      = aws_api_gateway_rest_api.api.id
  resource_id      = aws_api_gateway_resource.model.id
  api_key_required = false
  http_method      = "POST"
  authorization    = "NONE"
}

resource "aws_api_gateway_integration" "model" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.model.id
  http_method             = "POST"
  type                    = "AWS"
  integration_http_method = "POST"
  credentials             = aws_iam_role.api.arn
  uri                     = aws_lambda_function.ai-api-lambda.invoke_arn
  request_templates = {
    "application/json" = <<EOF
    {
      "username" :  "$context.authorizer.claims['cognito:username']"
    }
EOF
  }
}

resource "aws_api_gateway_method_response" "model_method_200" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.model.id
  http_method = aws_api_gateway_method.model.http_method
  status_code = "200"
  response_models = {
    "application/json" = "Empty"
  }
}

resource "aws_api_gateway_integration_response" "model_integration_200" {
  rest_api_id       = aws_api_gateway_rest_api.api.id
  resource_id       = aws_api_gateway_resource.model.id
  http_method       = aws_api_gateway_method.model.http_method
  status_code       = aws_api_gateway_method_response.model_method_200.status_code
}

# /ocr
resource "aws_api_gateway_method" "ocr" {
  rest_api_id      = aws_api_gateway_rest_api.api.id
  resource_id      = aws_api_gateway_resource.ocr.id
  api_key_required = false
  http_method      = "POST"
  authorization    = "COGNITO_USER_POOLS"
  authorizer_id    = aws_api_gateway_authorizer.cognito_authorizer.id
}

resource "aws_api_gateway_integration" "ocr" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.ocr.id
  http_method             = "POST"
  type                    = "AWS"
  integration_http_method = "POST"
  credentials             = aws_iam_role.api.arn
  uri                     = aws_lambda_function.ai-api-ocr.invoke_arn

  request_templates = {
    "application/json" = <<EOF
    {
      "username" :  "$context.authorizer.claims['cognito:username']"
    }
EOF
  }
}

resource "aws_api_gateway_method_response" "ocr_method_200" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.ocr.id
  http_method = aws_api_gateway_method.ocr.http_method
  status_code = "200"
  response_models = {
    "application/json" = "Empty"
  }
}

resource "aws_api_gateway_integration_response" "ocr_integration_200" {
  rest_api_id       = aws_api_gateway_rest_api.api.id
  resource_id       = aws_api_gateway_resource.ocr.id
  http_method       = aws_api_gateway_method.ocr.http_method
  status_code       = aws_api_gateway_method_response.ocr_method_200.status_code
}

# /prompt
resource "aws_api_gateway_method" "prompt" {
  rest_api_id      = aws_api_gateway_rest_api.api.id
  resource_id      = aws_api_gateway_resource.prompt.id
  api_key_required = false
  http_method      = "GET"
  authorization    = "COGNITO_USER_POOLS"
  authorizer_id    = aws_api_gateway_authorizer.cognito_authorizer.id
}

resource "aws_api_gateway_integration" "prompt" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.prompt.id
  http_method             = "GET"
  type                    = "AWS"
  integration_http_method = "POST"
  credentials             = aws_iam_role.api.arn
  uri                     = aws_lambda_function.ai-api-prompts.invoke_arn

  request_templates = {
    "application/json" = <<EOF
    {
      "username" :  "$context.authorizer.claims['cognito:username']"
    }
EOF
  }
}

resource "aws_api_gateway_method_response" "prompt_method_200" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.prompt.id
  http_method = aws_api_gateway_method.prompt.http_method
  status_code = "200"
  response_models = {
    "application/json" = "Empty"
  }
}

resource "aws_api_gateway_integration_response" "prompt_integration_200" {
  rest_api_id       = aws_api_gateway_rest_api.api.id
  resource_id       = aws_api_gateway_resource.prompt.id
  http_method       = aws_api_gateway_method.prompt.http_method
  status_code       = aws_api_gateway_method_response.prompt_method_200.status_code
}