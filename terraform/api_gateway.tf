resource "aws_api_gateway_rest_api" "api" {
  name        = "ai-api"
  description = "IIIF LLM API Gateway"
  endpoint_configuration {
    types = ["REGIONAL"]
  }
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
  type                    = "AWS_PROXY"
  integration_http_method = "POST"
  passthrough_behavior    = "NEVER"
  credentials             = aws_iam_role.api.arn
  uri                     = aws_lambda_function.ai-api-lambda.invoke_arn
}

# /ocr

resource "aws_api_gateway_method" "ocr" {
  rest_api_id      = aws_api_gateway_rest_api.api.id
  resource_id      = aws_api_gateway_resource.ocr.id
  api_key_required = false
  http_method      = "POST"
  authorization    = "NONE"
}

resource "aws_api_gateway_integration" "api" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.ocr.id
  http_method             = "POST"
  type                    = "AWS_PROXY"
  integration_http_method = "POST"
  passthrough_behavior    = "NEVER"
  credentials             = aws_iam_role.api.arn
  uri                     = aws_lambda_function.ai-api-ocr.invoke_arn
}

# /prompt

resource "aws_api_gateway_method" "prompt" {
  rest_api_id      = aws_api_gateway_rest_api.api.id
  resource_id      = aws_api_gateway_resource.prompt.id
  api_key_required = false
  http_method      = "POST"
  authorization    = "NONE"
}

resource "aws_api_gateway_integration" "prompt" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.prompt.id
  http_method             = "POST"
  type                    = "AWS_PROXY"
  integration_http_method = "POST"
  passthrough_behavior    = "NEVER"
  credentials             = aws_iam_role.api.arn
  uri                     = aws_lambda_function.ai-api-ocr.invoke_arn
}