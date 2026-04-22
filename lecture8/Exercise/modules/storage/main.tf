resource "random_id" "suffix" {
  for_each = toset(var.bucket_suffixes)

  byte_length = 4
}
resource "aws_s3_bucket" "pipeline" {
  for_each = toset(var.bucket_suffixes)

  bucket = "${var.project}-${var.env}-${each.key}-${random_id.suffix[each.key].hex}"
}

resource "aws_s3_bucket_versioning" "pipeline" {
  for_each = aws_s3_bucket.pipeline

  bucket = each.value.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "pipeline" {
  for_each = aws_s3_bucket.pipeline

  bucket = each.value.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}
