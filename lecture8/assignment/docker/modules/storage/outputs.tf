output "console_urls" {
  description = "MinIO console URLs by bucket"
  value       = { for k, v in docker_container.minio : k => "http://localhost:${var.buckets[k].console_port}" }
}

output "api_urls" {
  description = "MinIO API URLs by bucket"
  value       = { for k, v in docker_container.minio : k => "http://localhost:${var.buckets[k].api_port}" }
}
