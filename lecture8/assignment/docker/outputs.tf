output "minio_console_urls" {
  description = "MinIO console URLs by stage"
  value       = module.storage.console_urls
}

output "minio_api_urls" {
  description = "MinIO API URLs by stage"
  value       = module.storage.api_urls
}

output "postgres_port" {
  value = module.database.db_port
}

output "postgres_db_name" {
  value = module.database.db_name
}

output "postgres_connection_string" {
  value     = module.database.connection_string
  sensitive = true
}
