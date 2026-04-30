variable "buckets" {
  description = "Map of storage buckets to create"
  type = map(object({
    api_port     = number
    console_port = number
  }))
}

variable "minio_user" {
  description = "MinIO root user"
  type        = string
  default     = "minioadmin"
}

variable "minio_password" {
  description = "MinIO root password"
  type        = string
  sensitive   = true
  default     = "minioadmin"
}

variable "network_name" {
  description = "Docker network name"
  type        = string
}
