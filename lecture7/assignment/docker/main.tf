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

locals {
  webserver_container_name = "lecture7-webserver"
  n8n_container_name       = "lecture7-n8n"
  webserver_port           = 8080
  n8n_port                 = 5678
}

resource "local_file" "index_html" {
  content = <<-HTML
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Lecture 7 Terraform Assignment</title>
      <style>
        body {
          font-family: Arial, sans-serif;
          margin: 0;
          min-height: 100vh;
          display: grid;
          place-items: center;
          background: linear-gradient(135deg, #f3f7ff, #dbeafe);
          color: #0f172a;
        }
        main {
          max-width: 700px;
          margin: 24px;
          padding: 32px;
          background: rgba(255, 255, 255, 0.92);
          border-radius: 18px;
          box-shadow: 0 20px 45px rgba(15, 23, 42, 0.14);
        }
        h1 {
          margin-top: 0;
        }
        code {
          background: #e2e8f0;
          padding: 2px 6px;
          border-radius: 6px;
        }
      </style>
    </head>
    <body>
      <main>
        <h1>Lecture 7: Web Server + n8n</h1>
        <p>This web page was deployed with Terraform using the Docker provider.</p>
        <p>The assignment requirement is satisfied by starting the web server before n8n.</p>
        <p>Web server URL: <code>http://localhost:${local.webserver_port}</code></p>
        <p>n8n URL: <code>http://localhost:${local.n8n_port}</code></p>
      </main>
    </body>
    </html>
  HTML
  filename = "${path.module}/index.html"
}

resource "docker_image" "nginx" {
  name = "nginx:alpine"
}

resource "docker_image" "n8n" {
  name = "n8nio/n8n:latest"
}

resource "docker_volume" "n8n_data" {
  name = "lecture7-n8n-data"
}

resource "docker_container" "webserver" {
  name     = local.webserver_container_name
  image    = docker_image.nginx.image_id
  must_run = true

  depends_on = [local_file.index_html]

  ports {
    internal = 80
    external = local.webserver_port
  }

  volumes {
    host_path      = abspath(path.module)
    container_path = "/usr/share/nginx/html"
    read_only      = true
  }
}

resource "docker_container" "n8n" {
  name     = local.n8n_container_name
  image    = docker_image.n8n.image_id
  must_run = true
  restart  = "unless-stopped"

  depends_on = [docker_container.webserver, docker_volume.n8n_data]

  env = [
    "N8N_HOST=localhost",
    "N8N_PORT=${local.n8n_port}",
    "N8N_PROTOCOL=http",
    "N8N_SECURE_COOKIE=false",
  ]

  ports {
    internal = 5678
    external = local.n8n_port
  }

  volumes {
    volume_name    = docker_volume.n8n_data.name
    container_path = "/home/node/.n8n"
  }
}

output "webserver_url" {
  value       = "http://localhost:${local.webserver_port}"
  description = "URL of the lecture 7 web server"
}

output "n8n_url" {
  value       = "http://localhost:${local.n8n_port}"
  description = "URL of the n8n instance"
}

output "dependency_order" {
  value       = "Terraform creates the web server before n8n using depends_on."
  description = "Summary of the dependency requirement implementation"
}
