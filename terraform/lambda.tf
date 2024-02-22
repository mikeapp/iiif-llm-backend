
# Build layer with Python dependencies
data "archive_file" "python_layer" {
  type        = "zip"
  output_path = "/tmp/python_layer_zip_dir.zip"
  source_dir  = "../python_layer"
}

resource "aws_lambda_layer_version" "python_layer" {
  layer_name          = "python_dependencies"
  filename            = data.archive_file.python_layer.output_path
  source_code_hash    = data.archive_file.python_layer.output_base64sha256
  compatible_runtimes = ["python3.12"]
}

# Bundle Lambda code
data "archive_file" "lambda" {
  type        = "zip"
  output_path = "/tmp/lambda_api_zip_dir.zip"
  source_dir  = "../lambda_api"
}

# Create a Lambda
resource "aws_lambda_function" "ai-api-lambda" {
  filename         = data.archive_file.lambda.output_path
  source_code_hash = data.archive_file.lambda.output_base64sha256
  function_name    = "ai-api-lambda"
  role             = aws_iam_role.lambda_api_role.arn
  handler          = "api_handler.lambda_handler"
  runtime          = "python3.12"
  layers           = [aws_lambda_layer_version.python_layer.arn]
  timeout          = 25
  environment {
    variables = {
      "db" : var.db_url,
      "username" : "ai_user"
    }
  }
  vpc_config {
    subnet_ids         = [var.subnet_id]
    security_group_ids = [var.sg_id]
  }
}