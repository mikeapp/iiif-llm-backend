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

resource "aws_api_gateway_resource" "ocr" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_resource.api.id
  path_part   = "model"
}

resource "aws_api_gateway_resource" "ocr" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_resource.api.id
  path_part   = "prompt"
}

# OCR webhook API call

resource "aws_api_gateway_method" "api" {
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
  uri                     = aws_lambda_function.ai-api-lambda.invoke_arn

  request_parameters = {
    "integration.request.header.Content-Type" = "'application/x-www-form-urlencoded'"
  }

  request_templates = {
    "application/json" = "Action=SendMessage&MessageBody=$input.body"
  }
}

resource "aws_api_gateway_integration_response" "_200" {
  rest_api_id       = aws_api_gateway_rest_api.api.id
  resource_id       = aws_api_gateway_resource.ocr.id
  http_method       = aws_api_gateway_method.api.http_method
  status_code       = aws_api_gateway_method_response._200.status_code
  selection_pattern = "^2[0-9][0-9]"

  #response_templates = {
  #  "application/json" = "{\"message\": \"Message receeived\"}"
  #}

  depends_on = [aws_api_gateway_integration.api]
}

resource "aws_api_gateway_method_response" "_200" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.ocr.id
  http_method = aws_api_gateway_method.api.http_method
  status_code = 200

  #response_models = {
  #  "application/json" = "Empty"
  #}
}
