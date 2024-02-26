resource "aws_iam_role" "lambda_api_role" {
  name               = "lambda_api_role"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "basic" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  role       = aws_iam_role.lambda_api_role.name
}

# Additional Lambda policy
data "aws_iam_policy_document" "lambda_api_policy_document" {
  statement {
    effect    = "Allow"
    actions   = ["bedrock:InvokeModel"]
    resources = ["arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-text-express-v1"]
  }
  statement {
    effect    = "Allow"
    actions   = ["secretsmanager:GetSecretValue"]
    resources = [var.secrets]
  }
  statement {
    effect    = "Allow"
    actions   = ["textract:DetectDocumentText"]
    resources = ["*"]
  }
  statement {
    effect    = "Allow"
    actions   = ["states:StartExecution"]
    resources = [aws_sfn_state_machine.ai-api-state-machine.arn]
  }
  statement {
    effect = "Allow"
    actions = [
      "ec2:DescribeNetworkInterfaces",
      "ec2:CreateNetworkInterface",
      "ec2:DeleteNetworkInterface",
      "ec2:DescribeInstances",
      "ec2:AttachNetworkInterface"
    ]
    resources = ["*"]
  }
  statement {
    effect = "Allow"
    actions = ["s3:PutObject",
      "s3:GetObjectAcl",
      "s3:GetObject",
      "s3:GetObjectAttributes",
      "s3:GetObjectTagging",
    "s3:DeleteObject"]
    resources = ["${aws_s3_bucket.tmp_bucket.arn}/*"]
  }
}

resource "aws_iam_role_policy" "lambda_api_policies" {
  name   = "sender_sqs_policy"
  role   = aws_iam_role.lambda_api_role.name
  policy = data.aws_iam_policy_document.lambda_api_policy_document.json
}

# Role for Stap Functions
data "aws_iam_policy_document" "state_machine_assume_role_policy" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["states.amazonaws.com"]
    }

    actions = [
      "sts:AssumeRole",
    ]
  }
}

data "aws_iam_policy_document" "state_machine_role_policy" {
  statement {
    effect = "Allow"

    actions = [
      "lambda:InvokeFunction"
    ]

    resources = [
      "${aws_lambda_function.ai-api-s3-copy.arn}:*",
      "${aws_lambda_function.ai-api-textract.arn}:*"
    ]
  }

}

resource "aws_iam_role" "ai-api-text-step-function-role" {
  name               = "ai-api-text-step-function-role"
  assume_role_policy = data.aws_iam_policy_document.state_machine_assume_role_policy.json
}

resource "aws_iam_role_policy" "ai-api-text-step-function-role-policy" {
  role   = aws_iam_role.ai-api-text-step-function-role.id
  policy = data.aws_iam_policy_document.state_machine_role_policy.json
}


# API Gateway


# Allow Lambda Invocation by API Gateway
data "aws_iam_policy_document" "invocation_policy" {
  statement {
    effect    = "Allow"
    actions   = ["lambda:InvokeFunction"]
    resources = [
      aws_lambda_function.ai-api-ocr.arn,
      aws_lambda_function.ai-api-lambda.arn
    ]
  }
}

resource "aws_iam_role_policy" "invocation_policy" {
  name   = "default"
  role   = aws_iam_role.api.id
  policy = data.aws_iam_policy_document.invocation_policy.json
}

# API Gateway IAM

resource "aws_iam_role" "api" {
  name = "alma-api-role"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "apigateway.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_iam_policy" "api" {
  name = "my-api-perms"

  policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:DescribeLogGroups",
          "logs:DescribeLogStreams",
          "logs:PutLogEvents",
          "logs:GetLogEvents",
          "logs:FilterLogEvents"
        ],
        "Resource": "*"
      }
    ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "api" {
  role       = aws_iam_role.api.name
  policy_arn = aws_iam_policy.api.arn
}
