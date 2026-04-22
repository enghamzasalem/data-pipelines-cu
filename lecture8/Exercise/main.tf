terraform {
  required_version = ">= 1.0.0"

  required_providers {
    random = {
  source  = "hashicorp/random"
  version = "~> 3.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

module "storage" {
  source = "./modules/storage"

  project         = var.project
  env             = var.env
  bucket_suffixes = var.bucket_suffixes
}

module "database" {
  source = "./modules/database"

  project           = var.project
  env               = var.env
  create_database   = var.create_database
  db_instance_class = var.db_instance_class
  db_name           = var.db_name
  db_username       = var.db_username
  db_password       = var.db_password
}