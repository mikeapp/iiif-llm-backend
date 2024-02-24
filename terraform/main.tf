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


variable "subnet_id" {}
variable "sg_id" {}
variable "db_url" {}
variable "secrets" {}

# S3 bucket
resource "aws_s3_bucket" "tmp_bucket" {
  bucket = "iiif-api-temp"
}