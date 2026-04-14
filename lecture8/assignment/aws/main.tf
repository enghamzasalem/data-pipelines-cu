terraform {
  required_version = ">= 1.0.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

locals {
  common_tags = {
    Project = var.project
    Env     = var.env
    Lecture = "8"
  }
}

module "pipeline_buckets" {
  source = "./modules/s3-bucket"

  for_each = toset(var.bucket_suffixes)

  bucket_name = "${var.project}-${var.env}-${each.key}-${var.bucket_name_suffix}"
  tags        = merge(local.common_tags, { Stage = each.key })
}

resource "aws_dynamodb_table" "pipeline_metadata" {
  name         = "${var.project}-${var.env}-metadata"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "pipeline_id"

  attribute {
    name = "pipeline_id"
    type = "S"
  }

  server_side_encryption {
    enabled = true
  }

  tags = merge(local.common_tags, { Resource = "metadata-db" })
}
