output "minio_console_url" {
  value = module.storage.minio_url
}

output "bucket_names" {
  value = module.storage.bucket_names
}

output "postgres_connection" {
  value = module.database.connection_string
}