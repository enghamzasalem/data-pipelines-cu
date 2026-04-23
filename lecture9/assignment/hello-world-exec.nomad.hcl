job "hello-world" {
  type = "batch"

  group "app" {
    count = 1

    task "hello" {
      driver = "exec"

      config {
        command = "/bin/echo"
        args    = ["Hello, world from Nomad!"]
      }

      resources {
        cpu    = 1
        memory = 64
      }
    }
  }
}
