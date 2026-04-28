output "bucket_ids" {
  value = { for k, v in aws_s3_bucket.pipeline : k => v.id }
}

output "bucket_arns" {
  value = { for k, v in aws_s3_bucket.pipeline : k => v.arn }
}