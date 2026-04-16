terraform {
  required_providers {
    docker = {
      source = "kreuzwerker/docker"
      version = "~> 3.0"
    }
  }
}

resource "docker_container" "minio" {
  for_each = toset(["raw", "staged"])

  name  = "minio-${each.key}"
  image = "minio/minio:latest"

  env = [
    "MINIO_ROOT_USER=minioadmin",
    "MINIO_ROOT_PASSWORD=minioadmin"
  ]

  command = ["server", "/data", "--console-address", ":9001"]

  ports {
    internal = 9000
    external = each.key == "raw" ? 9000 : 9002
  }

  ports {
    internal = 9001
    external = each.key == "raw" ? 9001 : 9003
  }
}