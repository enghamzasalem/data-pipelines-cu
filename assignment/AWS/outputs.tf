output "bucket_names" {
  value = module.s3.bucket_names
}

output "bucket_arns" {
  value = module.s3.bucket_arns
}

output "rds_endpoint" {
  value = module.rds.endpoint
}