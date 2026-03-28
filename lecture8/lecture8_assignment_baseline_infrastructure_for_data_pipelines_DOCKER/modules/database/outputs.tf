output "container_id" {
  description = "PostgreSQL container ID"
  value       = docker_container.postgres.id
}

output "connection_string" {
  description = "PostgreSQL connection string"
  value       = "postgresql://${var.postgres_user}:${var.postgres_password}@localhost:${var.port}/${var.postgres_db}"
}

output "host" {
  description = "PostgreSQL host"
  value       = "localhost"
}

output "port" {
  description = "PostgreSQL port"
  value       = var.port
}

output "database_name" {
  description = "PostgreSQL database name"
  value       = var.postgres_db
}