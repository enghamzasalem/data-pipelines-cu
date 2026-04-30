terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
  }
  required_version = ">= 1.3.0"
}

provider "docker" {}

# ── Shared network ────────────────────────────────────────────────────────────
resource "docker_network" "lecture7_net" {
  name = "lecture7_net"
}

# ── Pull images ───────────────────────────────────────────────────────────────
resource "docker_image" "nginx" {
  name         = "nginx:alpine"
  keep_locally = false
}

resource "docker_image" "n8n" {
  name         = "n8nio/n8n:latest"
  keep_locally = false
}

# ── Web server container ──────────────────────────────────────────────────────
resource "docker_container" "webserver" {
  name  = "lecture7_webserver"
  image = docker_image.nginx.image_id

  ports {
    internal = 80
    external = 8080
  }

  networks_advanced {
    name = docker_network.lecture7_net.name
  }

  # Mount our custom landing page into nginx's default serve directory
  volumes {
    host_path      = abspath("${path.module}/index.html")
    container_path = "/usr/share/nginx/html/index.html"
    read_only      = true
  }

  restart = "unless-stopped"

  labels {
    label = "project"
    value = "lecture7"
  }
}

# ── n8n container ─────────────────────────────────────────────────────────────
# depends_on ensures webserver is created and running BEFORE n8n starts.
resource "docker_container" "n8n" {
  name  = "lecture7_n8n"
  image = docker_image.n8n.image_id

  # Terraform will create/start the webserver container first
  depends_on = [docker_container.webserver]

  ports {
    internal = 5678
    external = 5678
  }

  networks_advanced {
    name = docker_network.lecture7_net.name
  }

  env = [
    "N8N_HOST=localhost",
    "N8N_PORT=5678",
    "N8N_PROTOCOL=http",
    "WEBHOOK_URL=http://localhost:5678/",
    # Skip owner setup prompt so the UI opens immediately
    "N8N_USER_MANAGEMENT_DISABLED=true",
    "N8N_BASIC_AUTH_ACTIVE=false",
  ]

  restart = "unless-stopped"

  labels {
    label = "project"
    value = "lecture7"
  }
}
