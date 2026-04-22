terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# -----------------------------
# S3 MODULE (for_each)
# -----------------------------
module "s3" {
  source = "./modules/s3"

  project_name = var.project_name

  buckets = {
    raw     = "raw"
    staged  = "staged"
    curated = "curated"
  }
}

# -----------------------------
# RDS MODULE
# -----------------------------
module "rds" {
  source = "./modules/rds"

  db_name     = var.db_name
  db_user     = var.db_user
  db_password = var.db_password
}