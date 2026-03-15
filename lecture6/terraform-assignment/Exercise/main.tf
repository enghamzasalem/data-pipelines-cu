# Terraform Assignment: First Webserver (Local)
# Deploys a Docker container serving a simple HTML page on localhost:8080

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
  filename = "./index.html"
  content  = <<-EOT
    <!DOCTYPE html>
    <html>
    <head>
      <title>Terraform Assignment</title>
    </head>
    <body style="background-color: #f0f8ff; font-family: Arial; margin: 40px;">

      <h1>Terraform Web Page</h1>

      <p>
        This web page was created as part of my Terraform assignment.
        Terraform was used to deploy a web server using Docker and Nginx.
      </p>

      <h2>About Terraform</h2>

      <p>
        Terraform is a tool used to create and manage infrastructure using code.
        It helps in automating the setup of servers and services.
      </p>

      <h2>About Me</h2>

      <p>
        My name is Sri Sai Venkata Adithya. I am studying Data Engineering
        and learning tools such as Terraform, Docker, and Apache Airflow.
      </p>

      <h2>Course</h2>

      <p>
        Course: Data Pipeline Engineering
      </p>

    </body>
    </html>
  EOT
}

resource "docker_container" "webserver" {
  image    = docker_image.nginx.image_id
  name     = "terraform-assignment-webserver"
  must_run = true

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

output "local_url" {
  value       = "http://localhost:8080"
  description = "URL to access your deployed HTML page (local)"
}

output "container_name" {
  value       = docker_container.webserver.name
  description = "Docker container name"
}
