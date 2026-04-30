variable "container_name" {
  description = "PostgreSQL container name"
  type        = string
  default     = "pipeline-postgres"
}

variable "db_name" {
  description = "Database name"
  type        = string
  default     = "pipeline_metadata"
}

variable "db_user" {
  description = "Database user"
  type        = string
  default     = "pipeline_user"
}

variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
  default     = "pipeline_pass"
}

variable "db_port" {
  description = "Host port for PostgreSQL"
  type        = number
  default     = 5432
}

variable "network_name" {
  description = "Docker network name"
  type        = string
}
