terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
  }
}

provider "docker" {}

# -----------------------------
# STORAGE MODULE (MinIO)
# -----------------------------
module "storage" {
  source = "./modules/storage"

  project_name = var.project_name

  buckets = {
    raw    = "raw-data"
    staged = "staged-data"
  }
}

# -----------------------------
# DATABASE MODULE (Postgres)
# -----------------------------
module "database" {
  source = "./modules/database"

  db_name     = var.db_name
  db_user     = var.db_user
  db_password = var.db_password
}