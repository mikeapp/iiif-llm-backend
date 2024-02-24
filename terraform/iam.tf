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
    actions   = [
      "ec2:DescribeNetworkInterfaces",
      "ec2:CreateNetworkInterface",
      "ec2:DeleteNetworkInterface",
      "ec2:DescribeInstances",
      "ec2:AttachNetworkInterface"
    ]
    resources = ["*"]
  }
  statement {
    effect    = "Allow"
    actions   = ["s3:PutObject",
      "s3:GetObjectAcl",
      "s3:GetObject",
      "s3:GetObjectAttributes",
      "s3:GetObjectTagging",
      "s3:DeleteObject"]
    resources = [ "${aws_s3_bucket.tmp_bucket.arn}/*" ]
  }
}

resource "aws_iam_role_policy" "lambda_api_policies" {
  name   = "sender_sqs_policy"
  role   = aws_iam_role.lambda_api_role.name
  policy = data.aws_iam_policy_document.lambda_api_policy_document.json
}