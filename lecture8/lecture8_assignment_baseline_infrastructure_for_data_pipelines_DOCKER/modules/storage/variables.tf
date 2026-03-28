variable "container_name" {
  description = "Name of the MinIO container"
  type        = string
}

variable "image_tag" {
  description = "MinIO image tag"
  type        = string
  default     = "latest"
}

variable "root_user" {
  description = "MinIO root username"
  type        = string
  sensitive   = true
}

variable "root_password" {
  description = "MinIO root password"
  type        = string
  sensitive   = true
}

variable "ports" {
  description = "Port mappings for MinIO"
  type = object({
    api   = number
    console = number
  })
  default = {
    api     = 9000
    console = 9001
  }
}

variable "network_name" {
  description = "Docker network name"
  type        = string
}

variable "data_dir" {
  description = "Data directory for MinIO"
  type        = string
  default     = "/data"
}