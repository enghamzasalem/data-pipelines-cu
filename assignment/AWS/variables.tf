variable "aws_region" {
  default = "eu-central-1"
}

variable "project_name" {
  default = "data-pipeline"
}

variable "db_name" {
  default = "pipeline_db"
}

variable "db_user" {
  default = "admin"
}

variable "db_password" {
  sensitive = true
}