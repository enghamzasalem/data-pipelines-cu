job "hello-world" {
  datacenters = ["dc1"]
  type = "batch"

  group "hello-group" {
    task "hello" {
      driver = "docker"

      config {
        image = "busybox"
        command = "echo"
        args = ["Hello, world from Nomad!"]
      }

      resources {
        cpu    = 1
        memory = 64
      }
    }
  }
}