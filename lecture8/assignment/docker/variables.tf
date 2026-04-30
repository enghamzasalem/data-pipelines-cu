variable "project" {
  description = "Project name"
  type        = string
  default     = "data-pipeline"
}

variable "env" {
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "buckets" {
  description = "Storage buckets for pipeline stages"
  type = map(object({
    api_port     = number
    console_port = number
  }))
  default = {
    raw = {
      api_port     = 9000
      console_port = 9001
    }
    staged = {
      api_port     = 9002
      console_port = 9003
    }
  }
}

variable "minio_user" {
  type    = string
  default = "minioadmin"
}

variable "minio_password" {
  type      = string
  sensitive = true
  default   = "minioadmin"
}

variable "db_name" {
  type    = string
  default = "pipeline_metadata"
}

variable "db_user" {
  type    = string
  default = "pipeline_user"
}

variable "db_password" {
  type      = string
  sensitive = true
  default   = "pipeline_pass"
}

variable "db_port" {
  type    = number
  default = 5432
}
