terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
  }
}

provider "docker" {}

module "storage" {
  source = "./modules/storage"
}

resource "docker_container" "postgres" {
  name  = "postgres"
  image = "postgres:latest"

  env = [
    "POSTGRES_USER=admin",
    "POSTGRES_PASSWORD=admin",
    "POSTGRES_DB=mydb"
  ]

  ports {
    internal = 5432
    external = 5432
  }
}