terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }
}

resource "aws_s3_bucket" "buckets" {
  for_each = var.buckets

  bucket = "${var.project_name}-${each.value}-${random_id.suffix.hex}"
}

resource "random_id" "suffix" {
  byte_length = 4
}

# Enable versioning
resource "aws_s3_bucket_versioning" "versioning" {
  for_each = aws_s3_bucket.buckets

  bucket = each.value.id

  versioning_configuration {
    status = "Enabled"
  }
}

# Enable encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "encryption" {
  for_each = aws_s3_bucket.buckets

  bucket = each.value.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}