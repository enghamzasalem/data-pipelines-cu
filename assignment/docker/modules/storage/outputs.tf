output "minio_url" {
  value = "http://localhost:9001"
}

output "bucket_names" {
  value = values(var.buckets)
}