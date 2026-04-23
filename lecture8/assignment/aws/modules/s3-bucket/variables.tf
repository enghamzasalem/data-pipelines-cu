variable "bucket_name" {
  description = "Globally unique S3 bucket name"
  type        = string
}

variable "tags" {
  description = "Tags applied to the bucket resources"
  type        = map(string)
  default     = {}
}
