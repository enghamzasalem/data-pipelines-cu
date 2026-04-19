job "nginx-web" {
  datacenters = ["dc1"]

  group "web" {
    network {
      port "http" {
        static = 8080
      }
    }

    task "nginx" {
      driver = "docker"

      config {
        image = "nginx:latest"
        ports = ["http"]
      }
    }
  }
}