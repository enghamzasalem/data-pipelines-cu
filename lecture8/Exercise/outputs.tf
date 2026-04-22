output "bucket_ids" {
  value = module.storage.bucket_ids
}

output "bucket_arns" {
  value = module.storage.bucket_arns
}

output "db_endpoint" {
  value     = module.database.db_endpoint
  sensitive = true
}

output "db_address" {
  value = module.database.db_address
}