terraform {
  required_providers {
    docker = {
      source = "kreuzwerker/docker"
    }
  }
}

resource "docker_image" "minio" {
  name = "minio/minio"
}

resource "docker_container" "minio" {
  name  = "minio"
  image = docker_image.minio.image_id

  ports {
    internal = 9000
    external = 9000
  }

  ports {
    internal = 9001
    external = 9001
  }

  env = [
    "MINIO_ROOT_USER=minioadmin",
    "MINIO_ROOT_PASSWORD=minioadmin"
  ]

  command = ["server", "/data", "--console-address", ":9001"]
}

# -----------------------------
# BUCKETS USING for_each
# -----------------------------
resource "null_resource" "buckets" {
  for_each = var.buckets

  depends_on = [docker_container.minio]

  provisioner "local-exec" {
    command = <<EOT
sleep 5
docker exec minio sh -c "
mc alias set local http://localhost:9000 minioadmin minioadmin &&
mc mb local/${each.value} || true
"
EOT
  }
}