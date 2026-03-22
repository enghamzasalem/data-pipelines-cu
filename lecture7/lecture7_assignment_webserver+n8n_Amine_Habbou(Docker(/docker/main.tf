terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
  }
}

provider "docker" {
  host = "unix:///var/run/docker.sock"
}

# Create web content directory
resource "null_resource" "create_web_dir" {
  provisioner "local-exec" {
    command = "mkdir -p ${path.module}/webserver_content"
  }
}

# Web server container
resource "docker_container" "webserver" {
  name  = "lecture7-webserver"
  image = "nginx:alpine"
  
  ports {
    internal = 80
    external = 8081
  }
  
  volumes {
    container_path = "/usr/share/nginx/html/index.html"
    host_path      = abspath("${path.module}/webserver_content/index.html")
  }
  
  depends_on = [null_resource.create_web_dir]
}

# Create index.html AFTER directory exists
resource "local_file" "index_html" {
  filename = "${path.module}/webserver_content/index.html"
  content  = <<-EOF
<!DOCTYPE html>
<html>
<head>
    <title>Web Server - Lecture 7</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            padding: 50px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            margin: 0;
        }
        .container {
            background: rgba(255,255,255,0.1);
            padding: 30px;
            border-radius: 10px;
            display: inline-block;
            margin-top: 100px;
        }
        h1 { font-size: 3em; margin: 0; }
        p { font-size: 1.2em; }
        .status {
            color: #4ade80;
            font-weight: bold;
        }
        hr {
            margin: 20px 0;
            border: none;
            border-top: 1px solid rgba(255,255,255,0.3);
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>The webserver is running</h1>
        <p class="status">Terraform deployed successfully</p>
        <p>This web server is running via Docker provider.</p>
        <p>n8n workflow automation will start next...</p>
        <hr>
        <small>Lecture 7 Assignment - Web Server + n8n</small><br>
        <small>Created by: Amine Habbou</small>
    </div>
</body>
</html>
EOF

  depends_on = [null_resource.create_web_dir]
}

# n8n container (starts AFTER webserver)
resource "docker_container" "n8n" {
  name  = "lecture7-n8n"
  image = "n8nio/n8n:latest"
  
  ports {
    internal = 5678
    external = 5678
  }
  
  env = [
    "N8N_HOST=localhost",
    "N8N_PORT=5678",
    "N8N_PROTOCOL=http"
  ]
  
  # CRITICAL: n8n depends on webserver
  depends_on = [docker_container.webserver]
}

# Outputs
output "webserver_url" {
  description = "URL to access the web server"
  value       = "http://localhost:8081"
}

output "n8n_url" {
  description = "URL to access n8n"
  value       = "http://localhost:5678"
}

output "webserver_container" {
  description = "Webserver container name"
  value       = docker_container.webserver.name
}

output "n8n_container" {
  description = "n8n container name"
  value       = docker_container.n8n.name
}