output "project_info" {
  description = "Project information"
  value = {
    project_name = var.project_name
    environment  = var.environment
  }
}

output "storage_info" {
  description = "MinIO storage information"
  value = {
    api_endpoint   = module.storage.api_endpoint
    console_url    = module.storage.console_url
    console_credentials = {
      username = var.minio_root_user
      password = var.minio_root_password
    }
    buckets = [for bucket in var.buckets : "${var.project_name}-${var.environment}-${bucket}"]
  }
  sensitive = true
}

output "database_info" {
  description = "PostgreSQL database information"
  value = {
    connection_string = module.database.connection_string
    host              = module.database.host
    port              = module.database.port
    database_name     = module.database.database_name
    username          = var.postgres_user
  }
  sensitive = true
}

output "buckets_created" {
  description = "List of created buckets"
  value       = [for bucket in var.buckets : "${var.project_name}-${var.environment}-${bucket}"]
}

output "docker_network" {
  description = "Docker network name"
  value       = docker_network.pipeline_network.name
}