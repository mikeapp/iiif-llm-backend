
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

# LLM API handler
resource "aws_lambda_function" "ai-api-lambda" {
  filename         = data.archive_file.lambda.output_path
  source_code_hash = data.archive_file.lambda.output_base64sha256
  function_name    = "ai-api-lambda"
  role             = aws_iam_role.lambda_api_role.arn
  handler          = "api_handler.lambda_handler"
  runtime          = "python3.12"
  layers           = [aws_lambda_layer_version.python_layer.arn, "arn:aws:lambda:us-east-1:177933569100:layer:AWS-Parameters-and-Secrets-Lambda-Extension:11"]
  timeout          = 25
  vpc_config {
    subnet_ids         = [var.subnet_id]
    security_group_ids = [var.sg_id]
  }
}

# OCR Handler
resource "aws_lambda_function" "ai-api-ocr" {
  filename         = data.archive_file.lambda.output_path
  source_code_hash = data.archive_file.lambda.output_base64sha256
  function_name    = "ai-api-ocr"
  role             = aws_iam_role.lambda_api_role.arn
  handler          = "ocr_handler.lambda_handler"
  runtime          = "python3.12"
  layers           = [aws_lambda_layer_version.python_layer.arn, "arn:aws:lambda:us-east-1:177933569100:layer:AWS-Parameters-and-Secrets-Lambda-Extension:11"]
  timeout          = 25
  vpc_config {
    subnet_ids         = [var.subnet_id]
    security_group_ids = [var.sg_id]
  }
}

# Textract Handler
resource "aws_lambda_function" "ai-api-textract" {
  filename         = data.archive_file.lambda.output_path
  source_code_hash = data.archive_file.lambda.output_base64sha256
  function_name    = "ai-api-textract"
  role             = aws_iam_role.lambda_api_role.arn
  handler          = "textract_handler.lambda_handler"
  runtime          = "python3.12"
  layers           = [aws_lambda_layer_version.python_layer.arn, "arn:aws:lambda:us-east-1:177933569100:layer:AWS-Parameters-and-Secrets-Lambda-Extension:11"]
  timeout          = 25
  environment {
    variables = {
      "s3_bucket" : aws_s3_bucket.tmp_bucket.id
    }
  }
  vpc_config {
    subnet_ids         = [var.subnet_id]
    security_group_ids = [var.sg_id]
  }
}


# Bundle Lambda code for S3 Copy
data "archive_file" "lambda_s3" {
  type        = "zip"
  output_path = "/tmp/lambda_s3_copy_dir.zip"
  source_dir  = "../lambda_s3_copy"
}

resource "aws_lambda_function" "ai-api-s3-copy" {
  filename         = data.archive_file.lambda_s3.output_path
  source_code_hash = data.archive_file.lambda_s3.output_base64sha256
  function_name    = "ai-api-s3-copy"
  role             = aws_iam_role.lambda_api_role.arn
  handler          = "s3_copy.lambda_handler"
  runtime          = "python3.12"
  layers           = [aws_lambda_layer_version.python_layer.arn, "arn:aws:lambda:us-east-1:177933569100:layer:AWS-Parameters-and-Secrets-Lambda-Extension:11"]
  timeout          = 25
  environment {
    variables = {
      "s3_bucket" : aws_s3_bucket.tmp_bucket.id
    }
  }
}

