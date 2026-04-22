terraform {
  required_providers {
    docker = {
      source = "kreuzwerker/docker"
    }
  }
}

resource "docker_image" "postgres" {
  name = "postgres:15"
}

resource "docker_container" "postgres" {
  name  = "postgres"
  image = docker_image.postgres.image_id

  ports {
    internal = 5432
    external = 5432
  }

  env = [
    "POSTGRES_DB=${var.db_name}",
    "POSTGRES_USER=${var.db_user}",
    "POSTGRES_PASSWORD=${var.db_password}"
  ]
}