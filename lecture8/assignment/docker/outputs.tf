output "minio_console_raw" {
  value = "http://localhost:9001"
}

output "minio_console_staged" {
  value = "http://localhost:9003"
}

output "postgres_connection" {
  value = "postgresql://admin:admin@localhost:5432/mydb"
}nano variables.tf