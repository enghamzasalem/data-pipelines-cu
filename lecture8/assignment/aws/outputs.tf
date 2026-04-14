output "bucket_names" {
  description = "S3 bucket names by pipeline stage"
  value       = { for stage, mod in module.pipeline_buckets : stage => mod.bucket_name }
}

output "bucket_arns" {
  description = "S3 bucket ARNs by pipeline stage"
  value       = { for stage, mod in module.pipeline_buckets : stage => mod.bucket_arn }
}

output "database_name" {
  description = "Metadata database equivalent for the pipeline"
  value       = aws_dynamodb_table.pipeline_metadata.name
}

output "database_arn" {
  description = "ARN of the metadata database equivalent"
  value       = aws_dynamodb_table.pipeline_metadata.arn
}
