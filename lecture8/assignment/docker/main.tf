terraform {
  required_version = ">= 1.0.0"

  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
  }
}

provider "docker" {}

resource "docker_network" "pipeline_net" {
  name = "${var.project}-${var.env}-network"
}

module "storage" {
  source = "./modules/storage"

  buckets        = var.buckets
  minio_user     = var.minio_user
  minio_password = var.minio_password
  network_name   = docker_network.pipeline_net.name
}

module "database" {
  source = "./modules/database"

  container_name = "${var.project}-${var.env}-postgres"
  db_name        = var.db_name
  db_user        = var.db_user
  db_password    = var.db_password
  db_port        = var.db_port
  network_name   = docker_network.pipeline_net.name
}
