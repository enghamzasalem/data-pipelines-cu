output "bucket_names" {
  value = [for b in aws_s3_bucket.buckets : b.bucket]
}

output "bucket_arns" {
  value = [for b in aws_s3_bucket.buckets : b.arn]
}