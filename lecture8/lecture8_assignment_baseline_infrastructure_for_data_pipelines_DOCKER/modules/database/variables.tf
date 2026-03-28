variable "container_name" {
  description = "Name of the PostgreSQL container"
  type        = string
}

variable "image_tag" {
  description = "PostgreSQL image tag"
  type        = string
  default     = "15-alpine"
}

variable "postgres_user" {
  description = "PostgreSQL username"
  type        = string
  sensitive   = true
}

variable "postgres_password" {
  description = "PostgreSQL password"
  type        = string
  sensitive   = true
}

variable "postgres_db" {
  description = "PostgreSQL database name"
  type        = string
}

variable "port" {
  description = "PostgreSQL port"
  type        = number
  default     = 5432
}

variable "network_name" {
  description = "Docker network name"
  type        = string
}