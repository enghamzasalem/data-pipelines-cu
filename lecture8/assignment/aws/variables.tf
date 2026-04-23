variable "aws_region" {
  description = "AWS region used for the lecture 8 infrastructure"
  type        = string
  default     = "eu-west-1"
}

variable "project" {
  description = "Project name used in resource names"
  type        = string
  default     = "data-pipeline"
}

variable "env" {
  description = "Environment name used in resource names"
  type        = string
  default     = "dev"
}

variable "bucket_suffixes" {
  description = "Storage stages to create with for_each"
  type        = list(string)
  default     = ["raw", "staged", "curated"]
}

variable "bucket_name_suffix" {
  description = "Unique suffix added to bucket names to avoid global name conflicts"
  type        = string
  default     = "wezdar-cu"
}
