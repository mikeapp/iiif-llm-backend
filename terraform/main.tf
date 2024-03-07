terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.31"
    }
  }

  required_version = ">= 1.2.0"
}

provider "aws" {
  alias  = "current"
  region = "us-east-1"
}

data "aws_region" "current" {
  provider = aws.current
}

data "aws_caller_identity" "current" {}

locals  {
  account_id = data.aws_caller_identity.current.account_id
}

variable "subnet_id" {}
variable "sg_id" {}
variable "db_url" {}
variable "secrets" {}
variable "cognito_arn" {}

# S3 bucket
resource "aws_s3_bucket" "tmp_bucket" {
  bucket = "iiif-api-temp"
}

# Step function
resource "aws_sfn_state_machine" "ai-api-state-machine" {
  name     = "ai-api-text-state-machine"
  role_arn = aws_iam_role.ai-api-text-step-function-role.arn
  definition = templatefile("text_state_machine.tftp1", {
    s3_copy_lambda = aws_lambda_function.ai-api-s3-copy.function_name,
    textract_lambda    = aws_lambda_function.ai-api-textract.function_name
  })
}

