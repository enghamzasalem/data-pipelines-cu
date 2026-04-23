# Terraform Assignment: First Webserver (Local)
# Deploys a Docker container serving a simple HTML page on localhost:8081

terraform {
  required_version = ">= 1.0.0"

  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
    local = {
      source  = "hashicorp/local"
      version = "~> 2.0"
    }
  }
}

provider "docker" {}

resource "docker_image" "nginx" {
  name = "nginx:alpine"
}

resource "local_file" "index_html" {
  content = <<-HTML
    <!DOCTYPE html>
    <html>
    <head><title>Hello from Subhankar(subiswas@constructor.university)!</title></head>
    <body>
      <h1>Hello, my name is Subhankar Biswas, and this is my first webserver. it was done by just by running a .tf file that automates the whole infrastructure establishment process. it creates a docker container and run the webserver (nginx) image inside it and then run the html file--the website-- on that webserver</h1>
      <p>This page was deployed using Terraform (local Docker).</p>
    </body>
    </html>
  HTML
  filename = "${path.module}/index.html"
}

resource "docker_container" "webserver" {
  image    = docker_image.nginx.image_id
  name     = "terraform-assignment-webserver"
  must_run = true

  depends_on = [local_file.index_html]

  ports {
    internal = 80
    external = 8081
  }

  volumes {
    host_path      = abspath(path.module)
    container_path = "/usr/share/nginx/html"
    read_only      = true
  }
}

output "local_url" {
  value       = "http://localhost:8081"
  description = "URL to access your deployed HTML page (local)"
}

output "container_name" {
  value       = docker_container.webserver.name
  description = "Docker container name"
}