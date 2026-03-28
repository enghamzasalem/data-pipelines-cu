variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "data-pipeline"
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "minio_root_user" {
  description = "MinIO root username"
  type        = string
  default     = "miniioass8"
  sensitive   = true
}

variable "minio_root_password" {
  description = "MinIO root password"
  type        = string
  default     = "miniioass8"
  sensitive   = true
}

variable "postgres_password" {
  description = "PostgreSQL password"
  type        = string
  default     = "assignment8"
  sensitive   = true
}

variable "postgres_user" {
  description = "PostgreSQL username"
  type        = string
  default     = "amine"
}

variable "postgres_db" {
  description = "PostgreSQL database name"
  type        = string
  default     = "pipeline_metadata"
}

variable "buckets" {
  description = "List of bucket names to create"
  type        = list(string)
  default     = ["raw", "staged", "curated"]
}

variable "network_name" {
  description = "Docker network name"
  type        = string
  default     = "data-pipeline-network"
}