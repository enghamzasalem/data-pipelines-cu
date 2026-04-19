job "simple-html-web" {
  datacenters = ["dc1"]

  group "web" {
    network {
      port "http" {
        static = 8081
      }
    }

    task "server" {
      driver = "docker"

      config {
        image = "nginx:latest"
        ports = ["http"]
      }
    }
  }
}