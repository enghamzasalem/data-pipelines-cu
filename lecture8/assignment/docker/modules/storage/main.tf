terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
  }
}

resource "docker_image" "minio" {
  name = "minio/minio:latest"
}

resource "docker_container" "minio" {
  for_each = var.buckets

  name  = "minio-${each.key}"
  image = docker_image.minio.image_id

  command = ["server", "/data/${each.key}", "--console-address", ":9001"]

  env = [
    "MINIO_ROOT_USER=${var.minio_user}",
    "MINIO_ROOT_PASSWORD=${var.minio_password}"
  ]

  ports {
    internal = 9000
    external = each.value.api_port
  }

  ports {
    internal = 9001
    external = each.value.console_port
  }

  networks_advanced {
    name = var.network_name
  }
}
