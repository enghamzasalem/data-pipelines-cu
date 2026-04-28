output "bucket_ids" {
  value       = module.s3.bucket_ids
  description = "S3 bucket IDs by stage"
}

output "bucket_arns" {
  value       = module.s3.bucket_arns
  description = "S3 bucket ARNs by stage"
}

output "db_endpoint" {
  value       = var.create_database ? aws_db_instance.main[0].endpoint : null
  description = "RDS PostgreSQL endpoint (if enabled)"
  sensitive   = true
}

output "db_address" {
  value       = var.create_database ? aws_db_instance.main[0].address : null
  description = "RDS host address"
}
