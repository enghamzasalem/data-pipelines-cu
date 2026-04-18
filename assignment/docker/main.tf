terraform {  
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
    local = {
      source = "hashicorp/local"
    }
  }
}

provider "docker" {}

resource "docker_image" "nginx" {
  name = "nginx:alpine"
}

resource "local_file" "index_html" {
  content = "<h1>Hello Renuka</h1><p>Lecture 7 Assignment</p>"
  filename = "${path.module}/index.html"
}

resource "docker_container" "webserver" {
  name  = "webserver"
  image = docker_image.nginx.image_id

  depends_on = [local_file.index_html]

  ports {
    internal = 80
    external = 8080
  }

  volumes {
    host_path      = abspath(path.module)
    container_path = "/usr/share/nginx/html"
    read_only      = true
  }
}

resource "docker_image" "n8n" {
  name = "n8nio/n8n"
}

resource "docker_container" "n8n" {
  name  = "n8n"
  image = docker_image.n8n.image_id

  depends_on = [docker_container.webserver]

  ports {
    internal = 5678
    external = 5678
  }
}

output "webserver_url" {
  value = "http://localhost:8080"
}

output "n8n_url" {
  value = "http://localhost:5678"
}

