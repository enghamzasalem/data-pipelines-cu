resource "docker_volume" "minio_data" {
  name = "${var.container_name}-data"
}

resource "docker_container" "minio" {
  name  = var.container_name
  image = "minio/minio:${var.image_tag}"
  
  command = ["server", var.data_dir, "--console-address", ":${var.ports.console}"]
  
  env = [
    "MINIO_ROOT_USER=${var.root_user}",
    "MINIO_ROOT_PASSWORD=${var.root_password}"
  ]
  
  ports {
    internal = 9000
    external = var.ports.api
  }
  
  ports {
    internal = var.ports.console
    external = var.ports.console
  }
  
  volumes {
    volume_name    = docker_volume.minio_data.name
    container_path = var.data_dir
  }
  
  networks_advanced {
    name = var.network_name
  }
  
  restart = "unless-stopped"
  
  healthcheck {
    test     = ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
    interval = "30s"
    timeout  = "10s"
    retries  = 3
  }
}