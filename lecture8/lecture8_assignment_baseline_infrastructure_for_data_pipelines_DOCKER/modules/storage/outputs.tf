output "container_id" {
  description = "MinIO container ID"
  value       = docker_container.minio.id
}

output "api_endpoint" {
  description = "MinIO API endpoint"
  value       = "localhost:${docker_container.minio.ports[0].external}"
}

output "console_url" {
  description = "MinIO Console URL"
  value       = "http://localhost:${docker_container.minio.ports[1].external}"
}

output "container_name" {
  description = "MinIO container name"
  value       = docker_container.minio.name
}