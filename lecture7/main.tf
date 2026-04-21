terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
  }
}

provider "docker" {}


# Web Server (nginx)

resource "docker_image" "nginx" {
  name = "nginx:latest"
}

resource "docker_container" "webserver" {
  name  = "webserver"
  image = docker_image.nginx.image_id

  ports {
    internal = 80
    external = 8080
  }
}

# n8n

resource "docker_image" "n8n" {
  name = "n8nio/n8n"
}

resource "docker_container" "n8n" {
  name  = "n8n"
  image = docker_image.n8n.image_id

  ports {
    internal = 5678
    external = 5678
  }

  depends_on = [
    docker_container.webserver
  ]
}


output "webserver_url" {
  value = "http://localhost:8080"
}

output "n8n_url" {
  value = "http://localhost:5678"
}